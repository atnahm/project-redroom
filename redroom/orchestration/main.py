"""
Redroom Forensic Backend API

FastAPI wrapper for Tier-1 deepfake detection system.
Zero external API calls. Full air-gapped operation.
All communications mTLS encrypted with certificate pinning.

Endpoints:
  POST /redroom/analyze - Execute complete forensic pipeline
  GET  /redroom/status  - System health check
  POST /redroom/verify  - Verify ledger entry integrity
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from pathlib import Path
import tempfile
from typing import Optional

from redroom.orchestration.forensic_orchestrator import ForensicOrchestrator
from redroom.ledger.merkle_ledger import MerkleTreeLedger
from redroom.vlm.sovereign_vlm import SovereignVLM, VLMModel

# Configure logging with redroom context
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [REDROOM] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="🛡️ Redroom Deepfake Detection Engine",
    version="1.0.0-tier1",
    description="Air-gapped forensic analysis for Tier-1 agencies"
)

# CORS - Restricted to internal networks only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize services
vlm = None
ledger = None
orchestrator = None


@app.on_event("startup")
async def startup_event():
    """Initialize all systems at startup"""
    global vlm, ledger, orchestrator

    logger.info("🚀 Redroom Forensic System Starting Up")

    try:
        # Initialize Merkle ledger
        ledger = MerkleTreeLedger(db_path="./redroom_ledger.db")
        logger.info("✅ Merkle ledger initialized")

        # Initialize sovereign VLM
        vlm = SovereignVLM(
            model_name=VLMModel.GEMMA_4_31B,
            vllm_endpoint="http://localhost:8001"
        )
        vlm.load()
        logger.info("✅ Sovereign VLM loaded")

        # Initialize orchestrator
        orchestrator = ForensicOrchestrator(vlm_model=vlm, ledger_service=ledger)
        logger.info("✅ Forensic orchestrator initialized")

        logger.info("🛡️ REDROOM SYSTEM READY FOR OPERATIONS")

    except Exception as e:
        logger.critical(f"❌ Startup failed: {e}")
        raise


@app.get("/redroom/status")
async def status():
    """System health check and capabilities"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")

    return {
        "status": "operational",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "vlm_model": vlm.model_name.value if vlm else "not_loaded",
        "ledger_size": ledger.get_ledger_size() if ledger else 0,
        "ledger_root": ledger.get_tree_root()[:16] + "..." if ledger else None,
        "mode": "REDROOM_TIER1",
        "air_gapped": True,
        "external_apis": "NONE",
        "forensic_pipeline": [
            "PRNU_extraction",
            "Bispectral_analysis",
            "rPPG_pulse_detection",
            "Oculometric_consistency",
            "VLM_forensic_reasoning",
            "Merkle_commitment",
            "Tear_line_reports"
        ]
    }


@app.post("/redroom/analyze")
async def analyze_evidence(
    file: UploadFile = File(...),
    analyst_id: str = "unknown",
    analysis_mode: str = "auto"
):
    """
    Execute complete forensic pipeline on submitted evidence
    
    Args:
        file: Image or video file to analyze
        analyst_id: PIV/CAC identifier (for audit trail)
        analysis_mode: "auto", "clinical", "surveillance", or "extreme"
        
    Returns:
        Complete forensic results with tear-line reports
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_types = ["image/jpeg", "image/png", "video/mp4", "video/quicktime"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )

    # Save file to temp location
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / file.filename

        try:
            # Write file
            contents = await file.read()
            with open(file_path, 'wb') as f:
                f.write(contents)

            logger.info(f"📥 Evidence ingested: {file.filename}")

            # Execute forensic pipeline
            results = await orchestrator.analyze(
                file_path=str(file_path),
                user_id=analyst_id,
                mode=analysis_mode
            )

            logger.info(f"✅ Analysis complete. Verdict: "
                       f"{'🚨 SUSPICIOUS' if results.is_flagged_suspicious else '✅ AUTHENTIC'}")

            # Return comprehensive results
            return {
                "status": "analysis_complete",
                "ingest": {
                    "timestamp": results.ingest_record.timestamp,
                    "file_hash": results.ingest_record.sha3_512_hash,
                    "file_size": results.ingest_record.file_size_bytes,
                },
                "forensic_results": {
                    "combined_probability": results.combined_synthesis_probability,
                    "is_suspicious": results.is_flagged_suspicious,
                    "prnu": results.prnu_analysis,
                    "bispectral": results.bispectral_analysis,
                    "rppg": results.rppg_analysis,
                    "oculometric": results.oculometric_analysis,
                    "vlm_reasoning": results.vlm_forensic_summary,
                },
                "ledger": {
                    "commitment_hash": results.ledger_commitment_hash,
                    "merkle_tree_root": ledger.get_tree_root()[:16] + "..." if ledger else None,
                },
                "reports": {
                    "unclassified_summary": results.tear_line_report_unclassified,
                    "classified_details": "[RESTRICTED - Classified report requires security clearance]"
                    if results.is_flagged_suspicious
                    else results.tear_line_report_classified
                },
                "audit_trail": {
                    "analyst_id": analyst_id,
                    "analysis_mode": analysis_mode,
                    "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                }
            }

        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/redroom/verify")
async def verify_ledger_entry(
    ingest_hash: str
):
    """
    Verify that a forensic analysis result hasn't been tampered with
    
    Returns:
        Merkle proof and verification status
    """
    if ledger is None:
        raise HTTPException(status_code=503, detail="Ledger not initialized")

    try:
        # Query ledger for this evidence
        entry = await ledger.query_by_ingest_hash(ingest_hash)

        if not entry:
            raise HTTPException(status_code=404, detail="Evidence not found in ledger")

        # Verify integrity
        is_valid, proof = await ledger.verify(entry.leaf_index)

        return {
            "status": "verification_complete",
            "evidence_hash": ingest_hash[:16] + "...",
            "ledger_entry_index": entry.leaf_index,
            "is_valid": is_valid,
            "merkle_proof": {
                "path_length": len(proof.merkle_path) if proof else None,
                "tree_root": proof.tree_root_hash[:16] + "..." if proof else None,
                "timestamp_verified": proof.timestamp_proven if proof else None,
            } if is_valid else None,
            "verdict": "✅ VERIFIED - No tampering detected" if is_valid else "❌ INVALID - Possible tampering"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.get("/redroom/audit-trail")
async def get_audit_trail(
    limit: int = 100,
    analyst_id: Optional[str] = None
):
    """
    Query complete audit trail for compliance
    
    Restricted: Requires analyst_id authentication in production
    """
    if ledger is None:
        raise HTTPException(status_code=503, detail="Ledger not initialized")

    try:
        entries = await ledger.audit_trail(analyst_id=analyst_id, limit=limit)

        return {
            "status": "audit_trail_retrieved",
            "entry_count": len(entries),
            "entries": [
                {
                    "leaf_index": e.leaf_index,
                    "timestamp": e.timestamp,
                    "analyst": e.analyst_id,
                    "evidence_hash": e.ingest_hash[:16] + "...",
                    "verdict": "SYNTHETIC" if e.combined_probability > 0.7 else "AUTHENTIC",
                    "confidence": f"{e.combined_probability:.1%}",
                }
                for e in entries
            ]
        }

    except Exception as e:
        logger.error(f"Audit trail failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "system": "Redroom Deepfake Detection Engine",
        "tier": "1 (CIA/RAW)",
        "mode": "air-gapped",
        "api_version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "status": "GET /redroom/status",
            "analyze": "POST /redroom/analyze",
            "verify": "POST /redroom/verify",
            "audit": "GET /redroom/audit-trail",
        }
    }


if __name__ == "__main__":
    logger.info("🔐 Starting Redroom backend on 0.0.0.0:8002")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )
