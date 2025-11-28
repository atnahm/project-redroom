// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SourceRegistry {
    mapping(string => bool) private mediaHashes;
    event MediaRegistered(string pHash, address indexed registrar);

    function registerMedia(string memory _pHash) public {
        require(!mediaHashes[_pHash], "Media already registered");
        mediaHashes[_pHash] = true;
        emit MediaRegistered(_pHash, msg.sender);
    }

    function verifyMedia(string memory _pHash) public view returns (bool) {
        return mediaHashes[_pHash];
    }
}
