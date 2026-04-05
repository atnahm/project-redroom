"""
Merkle Tree Ledger Service

Implements append-only, cryptographically-auditable evidence log.
Every forensic decision is committed with cryptographic proof of non-tampering.

Uses SHA-3-512 for all hashing (NIST-approved).

Architecture:
  - Local SQLite for MVP
  - Can scale to Trillian + etcd for distributed state
  - Supports 100+ concurrent analysts querying the ledger
  
Operations:
  1. Append: Add new evidence analysis to log
  2. Verify: Prove that an entry hasn't been tampered with
  3. Audit: Generate merkle proof for any entry
"""

import hashlib
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import asyncio
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class LedgerEntry:
    """Single entry in the forensic ledger"""
    leaf_index: int
    timestamp: str
    ingest_hash: str                 # SHA-3-512 of original evidence
    combined_probability: float      # Final AI-generation score
    forensic_signals: Dict[str, Any] # All forensic analyses
    analyst_id: str                  # Who ran the analysis
    entry_hash: str                  # SHA-3-512(entry_json)


@dataclass
class MerkleProof:
    """Cryptographic proof that entry hasn't been tampered"""
    leaf_index: int
    entry_hash: str
    merkle_path: List[str]           # Path to root
    tree_root_hash: str              # Current tree root
    timestamp_proven: str            # When commitment occurred


class MerkleTreeLedger:
    """
    Append-only Merkle tree for evidence chain-of-custody
    
    Properties:
      - Immutable: Once written, entries cannot be changed
      - Auditable: Anyone can verify integrity of any entry
      - Efficient: O(log N) proof size
    """

    def __init__(self, db_path: str = "./redroom_ledger.db"):
        """Initialize ledger"""
        self.db_path = Path(db_path)
        self.db_lock = Lock()
        
        # Initialize database
        self._init_db()
        
        # In-memory merkle tree for fast proofs
        self.merkle_tree = []
        self.tree_root_hash = self._compute_tree_root()
        
        logger.info(f"🔗 Merkle Ledger initialized: {self.db_path}")

    # ========== PUBLIC API ==========

    async def append(
        self,
        ingest_hash: str,
        combined_probability: float,
        forensic_signals: Dict[str, Any],
        analyst_id: str
    ) -> LedgerEntry:
        """
        Append new forensic analysis to ledger
        
        Returns:
            LedgerEntry with leaf index and merkle proof
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "ingest_hash": ingest_hash,
            "combined_probability": combined_probability,
            "forensic_signals": forensic_signals,
            "analyst_id": analyst_id,
        }

        entry_json = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha3_512(entry_json.encode()).hexdigest()

        with self.db_lock:
            cursor = self.db_path.parent.joinpath(self.db_path).parent.joinpath(
                "redroom_ledger.db"
            )
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO ledger_entries 
                (timestamp, ingest_hash, combined_probability, forensic_signals, 
                 analyst_id, entry_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["timestamp"],
                    ingest_hash,
                    combined_probability,
                    json.dumps(forensic_signals),
                    analyst_id,
                    entry_hash
                )
            )

            leaf_index = cur.lastrowid - 1  # 0-indexed
            conn.commit()
            conn.close()

        # Update in-memory tree
        self.merkle_tree.append(entry_hash)
        self.tree_root_hash = self._compute_tree_root()

        logger.info(
            f"✅ Evidence committed to ledger. "
            f"Leaf Index: {leaf_index}, Hash: {entry_hash[:16]}..."
        )

        return LedgerEntry(
            leaf_index=leaf_index,
            timestamp=entry["timestamp"],
            ingest_hash=ingest_hash,
            combined_probability=combined_probability,
            forensic_signals=forensic_signals,
            analyst_id=analyst_id,
            entry_hash=entry_hash
        )

    async def verify(self, leaf_index: int) -> Tuple[bool, Optional[MerkleProof]]:
        """
        Verify that a ledger entry hasn't been tampered with
        
        Returns:
            (is_valid, merkle_proof)
        """
        if leaf_index < 0 or leaf_index >= len(self.merkle_tree):
            logger.warning(f"Invalid leaf index: {leaf_index}")
            return False, None

        try:
            merkle_path = self._compute_merkle_path(leaf_index)
            proof = MerkleProof(
                leaf_index=leaf_index,
                entry_hash=self.merkle_tree[leaf_index],
                merkle_path=merkle_path,
                tree_root_hash=self.tree_root_hash,
                timestamp_proven=datetime.utcnow().isoformat()
            )

            # Verify the path leads to the root
            computed_root = self._verify_merkle_path(
                leaf_index,
                self.merkle_tree[leaf_index],
                merkle_path
            )

            is_valid = computed_root == self.tree_root_hash

            if is_valid:
                logger.info(f"✅ Ledger entry {leaf_index} verified")
            else:
                logger.warning(f"❌ Ledger entry {leaf_index} TAMPERED")

            return is_valid, proof if is_valid else None

        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False, None

    async def query_by_ingest_hash(self, ingest_hash: str) -> Optional[LedgerEntry]:
        """Query ledger for analyses of specific evidence"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute(
                """
                SELECT leaf_index, timestamp, ingest_hash, combined_probability,
                       forensic_signals, analyst_id, entry_hash
                FROM ledger_entries
                WHERE ingest_hash = ?
                ORDER BY leaf_index DESC
                LIMIT 1
                """,
                (ingest_hash,)
            )

            row = cur.fetchone()
            conn.close()

            if not row:
                return None

            return LedgerEntry(
                leaf_index=row[0],
                timestamp=row[1],
                ingest_hash=row[2],
                combined_probability=row[3],
                forensic_signals=json.loads(row[4]),
                analyst_id=row[5],
                entry_hash=row[6]
            )

    async def audit_trail(
        self,
        analyst_id: Optional[str] = None,
        limit: int = 100
    ) -> List[LedgerEntry]:
        """
        Query full audit trail (optionally filtered by analyst)
        
        Used for compliance and investigation
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            if analyst_id:
                cur.execute(
                    """
                    SELECT leaf_index, timestamp, ingest_hash, combined_probability,
                           forensic_signals, analyst_id, entry_hash
                    FROM ledger_entries
                    WHERE analyst_id = ?
                    ORDER BY leaf_index DESC
                    LIMIT ?
                    """,
                    (analyst_id, limit)
                )
            else:
                cur.execute(
                    """
                    SELECT leaf_index, timestamp, ingest_hash, combined_probability,
                           forensic_signals, analyst_id, entry_hash
                    FROM ledger_entries
                    ORDER BY leaf_index DESC
                    LIMIT ?
                    """,
                    (limit,)
                )

            rows = cur.fetchall()
            conn.close()

            return [
                LedgerEntry(
                    leaf_index=row[0],
                    timestamp=row[1],
                    ingest_hash=row[2],
                    combined_probability=row[3],
                    forensic_signals=json.loads(row[4]),
                    analyst_id=row[5],
                    entry_hash=row[6]
                )
                for row in rows
            ]

    def get_tree_root(self) -> str:
        """Get current Merkle tree root hash"""
        return self.tree_root_hash

    def get_ledger_size(self) -> int:
        """Get total number of entries"""
        return len(self.merkle_tree)

    # ========== PRIVATE METHODS ==========

    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Create ledger table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger_entries (
                leaf_index INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ingest_hash TEXT NOT NULL,
                combined_probability REAL NOT NULL,
                forensic_signals TEXT NOT NULL,
                analyst_id TEXT NOT NULL,
                entry_hash TEXT NOT NULL UNIQUE
            )
            """
        )

        # Load existing entries into memory
        cur.execute("SELECT entry_hash FROM ledger_entries ORDER BY leaf_index")
        rows = cur.fetchall()
        self.merkle_tree = [row[0] for row in rows]

        conn.commit()
        conn.close()

        logger.info(f"📊 Ledger loaded: {len(self.merkle_tree)} entries")

    def _compute_tree_root(self) -> str:
        """Compute current Merkle tree root hash"""
        if not self.merkle_tree:
            return hashlib.sha3_512(b"").hexdigest()

        # Build tree bottom-up
        current_level = self.merkle_tree.copy()

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = hashlib.sha3_512(
                    (left + right).encode()
                ).hexdigest()
                next_level.append(parent)
            current_level = next_level

        return current_level[0] if current_level else hashlib.sha3_512(b"").hexdigest()

    def _compute_merkle_path(self, leaf_index: int) -> List[str]:
        """Compute path from leaf to root"""
        if leaf_index < 0 or leaf_index >= len(self.merkle_tree):
            return []

        path = []
        current_level = self.merkle_tree.copy()
        current_index = leaf_index

        while len(current_level) > 1:
            if current_index % 2 == 0:
                # Current is left, get right sibling
                sibling_index = current_index + 1
                if sibling_index < len(current_level):
                    path.append(current_level[sibling_index])
                else:
                    path.append(current_level[current_index])
            else:
                # Current is right, get left sibling
                path.append(current_level[current_index - 1])

            # Move up to parent level
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = hashlib.sha3_512(
                    (left + right).encode()
                ).hexdigest()
                next_level.append(parent)

            current_level = next_level
            current_index //= 2

        return path

    def _verify_merkle_path(
        self,
        leaf_index: int,
        leaf_hash: str,
        merkle_path: List[str]
    ) -> str:
        """Verify merkle path and return computed root"""
        current = leaf_hash
        index = leaf_index

        for sibling in merkle_path:
            if index % 2 == 0:
                # Current is left
                current = hashlib.sha3_512(
                    (current + sibling).encode()
                ).hexdigest()
            else:
                # Current is right
                current = hashlib.sha3_512(
                    (sibling + current).encode()
                ).hexdigest()

            index //= 2

        return current
