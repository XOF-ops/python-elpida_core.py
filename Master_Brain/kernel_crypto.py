"""
Master_Brain Cryptographic Kernel
Implements immutable kernel signing, verification, and integrity checking.

The kernel is signed once at initialization and never modified.
All governance and pattern execution refers back to the kernel signature.
"""

import hashlib
import hmac
import json
from typing import Dict, Tuple, Optional
from datetime import datetime
import base64

# ============================================================================
# KERNEL SIGNATURE GENERATION
# ============================================================================

class KernelSigner:
    """Signs and verifies the immutable kernel"""

    def __init__(self, secret_key: str):
        """
        Initialize with secret key.
        Secret key should be:
        - At least 64 characters
        - Stored in hardware security module (HSM) in production
        - Rotated annually
        - Never logged or exposed
        """
        self.secret_key = secret_key
        self.algorithm = "SHA256"

    def sign_kernel(self, axioms: Dict, core_patterns: Dict) -> Tuple[str, str]:
        """
        Sign the immutable kernel (axioms + core patterns P001–P010).
        Returns (signature, kernel_hash).
        
        Called once at system initialization.
        """
        kernel_data = {
            "component": "KERNEL_IMMUTABLE",
            "version": "3.5",
            "timestamp": datetime.utcnow().isoformat(),
            "axioms": axioms,
            "core_patterns": core_patterns,
            "algorithm": self.algorithm
        }

        # Serialize deterministically (sorted keys)
        kernel_json = json.dumps(kernel_data, sort_keys=True, separators=(',', ':'))
        kernel_hash = hashlib.sha256(kernel_json.encode()).hexdigest()

        # HMAC signature
        signature = hmac.new(
            self.secret_key.encode(),
            kernel_json.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature, kernel_hash

    def create_kernel_sig_file(self, axioms: Dict, core_patterns: Dict, 
                               output_path: str = "kernel/kernel.sig"):
        """Create and save kernel.sig file"""
        signature, kernel_hash = self.sign_kernel(axioms, core_patterns)

        sig_file = {
            "kernel_component": "MASTER_BRAIN_IMMUTABLE",
            "version": "3.5",
            "kernel_hash": kernel_hash,
            "kernel_signature": signature,
            "signed_at": datetime.utcnow().isoformat(),
            "algorithm": "HMAC-SHA256",
            "note": "This signature proves kernel integrity. Do not modify."
        }

        with open(output_path, 'w') as f:
            json.dump(sig_file, f, indent=2)

        print(f"[KernelSigner] Kernel signed and saved to {output_path}")
        print(f"[KernelSigner] Kernel hash: {kernel_hash}")
        print(f"[KernelSigner] Signature: {signature[:32]}... (truncated)")

        return sig_file

# ============================================================================
# KERNEL VERIFICATION
# ============================================================================

class KernelVerifier:
    """Verifies kernel integrity"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def verify_kernel(self, axioms: Dict, core_patterns: Dict, 
                      expected_signature: str) -> bool:
        """
        Verify kernel signature matches expected.
        
        Returns True if kernel is unmodified, False if tampered.
        """
        kernel_data = {
            "component": "KERNEL_IMMUTABLE",
            "version": "3.5",
            "timestamp": datetime.utcnow().isoformat(),  # NOTE: timestamp will differ
            "axioms": axioms,
            "core_patterns": core_patterns,
            "algorithm": "SHA256"
        }

        # Reconstruct signature (excluding timestamp which will differ)
        kernel_data_for_sig = {
            "component": "KERNEL_IMMUTABLE",
            "version": "3.5",
            "axioms": axioms,
            "core_patterns": core_patterns,
            "algorithm": "SHA256"
        }

        kernel_json = json.dumps(kernel_data_for_sig, sort_keys=True, separators=(',', ':'))
        
        expected_sig = hmac.new(
            self.secret_key.encode(),
            kernel_json.encode(),
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected_sig, expected_signature)

        return is_valid

    def verify_kernel_from_file(self, axioms: Dict, core_patterns: Dict,
                                sig_file_path: str = "kernel/kernel.sig") -> Tuple[bool, str]:
        """
        Verify kernel against stored signature file.
        
        Returns (is_valid, message)
        """
        try:
            with open(sig_file_path, 'r') as f:
                sig_data = json.load(f)
        except FileNotFoundError:
            return False, f"Signature file not found: {sig_file_path}"

        expected_signature = sig_data.get("kernel_signature")
        if not expected_signature:
            return False, "No kernel signature in sig file"

        is_valid = self.verify_kernel(axioms, core_patterns, expected_signature)

        if is_valid:
            message = "✓ Kernel signature verified. Axioms and core patterns are unmodified."
            return True, message
        else:
            message = "✗ KERNEL COMPROMISED. Signature mismatch. Do not proceed."
            return False, message

# ============================================================================
# GNOSIS BLOCK SIGNING
# ============================================================================

class GnosisBlockSigner:
    """Sign individual Gnosis blocks (decision records)"""

    def __init__(self, signer_id: str, private_key: str):
        """
        Initialize signer with identity and private key.
        
        signer_id: e.g., "council_member_alice"
        private_key: HMAC secret (should be unique per signer)
        """
        self.signer_id = signer_id
        self.private_key = private_key

    def sign_gnosis_block(self, block_data: Dict) -> str:
        """
        Sign a Gnosis block.
        
        Block structure:
        {
            "id": "...",
            "pattern_ids": [...],
            "input_data": {...},
            "output_analysis": {...},
            "outcome": "...",
            "timestamp": "...",
            "quality_score": 0-7,
            "validated_by": [...],
            "notes": "..."
        }
        
        Note: 'signature' field should be omitted from block_data before signing.
        """
        # Create copy without signature
        data_to_sign = {k: v for k, v in block_data.items() if k != 'signature'}
        
        # Deterministic serialization
        json_str = json.dumps(data_to_sign, sort_keys=True, separators=(',', ':'), default=str)
        
        # Sign
        signature = hmac.new(
            self.private_key.encode(),
            json_str.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def sign_and_record(self, block_data: Dict) -> Dict:
        """
        Sign block and add signature to record.
        Returns complete block with signature.
        """
        signature = self.sign_gnosis_block(block_data)
        
        block_data["signature"] = signature
        block_data["signed_by"] = self.signer_id
        block_data["signed_at"] = datetime.utcnow().isoformat()

        return block_data

# ============================================================================
# GNOSIS BLOCK VERIFICATION
# ============================================================================

class GnosisBlockVerifier:
    """Verify Gnosis block signatures"""

    @staticmethod
    def verify_block(block_data: Dict, signer_public_key: str, signer_id: str) -> bool:
        """
        Verify a Gnosis block signature.
        
        In production, public_key would be retrieved from a public key infrastructure.
        For HMAC, we need the signer's public key (derived from private key).
        
        Note: HMAC is symmetric; for true public-key verification, use RSA/ECDSA.
        """
        stored_signature = block_data.get("signature")
        if not stored_signature:
            return False

        # Reconstruct original data (exclude signature field)
        data_for_verification = {k: v for k, v in block_data.items() 
                                 if k not in ['signature', 'signed_by', 'signed_at']}

        json_str = json.dumps(data_for_verification, sort_keys=True, 
                             separators=(',', ':'), default=str)

        # Recompute signature
        expected_signature = hmac.new(
            signer_public_key.encode(),
            json_str.encode(),
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison
        is_valid = hmac.compare_digest(stored_signature, expected_signature)

        return is_valid

    @staticmethod
    def verify_multi_signature(block_data: Dict, signers: Dict[str, str]) -> Tuple[bool, int, int]:
        """
        Verify multiple signatures on a block.
        
        signers: Dict of {signer_id: public_key}
        
        Returns (all_valid, valid_count, total_count)
        """
        stored_signatures = block_data.get("signatures", {})
        valid_count = 0

        for signer_id, public_key in signers.items():
            if signer_id in stored_signatures:
                stored_sig = stored_signatures[signer_id]
                
                # Verify this signature
                data_for_verification = {k: v for k, v in block_data.items() 
                                        if k not in ['signature', 'signatures', 'signed_by', 'signed_at']}

                json_str = json.dumps(data_for_verification, sort_keys=True, 
                                     separators=(',', ':'), default=str)

                expected_sig = hmac.new(
                    public_key.encode(),
                    json_str.encode(),
                    hashlib.sha256
                ).hexdigest()

                if hmac.compare_digest(stored_sig, expected_sig):
                    valid_count += 1

        total_count = len(signers)
        all_valid = (valid_count == total_count)

        return all_valid, valid_count, total_count

# ============================================================================
# PUBLIC KEY INFRASTRUCTURE (PKI) STUB
# ============================================================================

class MasterBrainPKI:
    """
    Public Key Infrastructure for Master_Brain.
    
    In production, this would integrate with:
    - HSM (Hardware Security Module) for key storage
    - Certificate authority for key rotation
    - LDAP/Active Directory for identity verification
    - Blockchain for immutable key registry
    """

    def __init__(self):
        self.signers = {}  # signer_id -> {public_key, certificate, valid_until}

    def register_signer(self, signer_id: str, public_key: str, 
                       valid_until: str = None) -> bool:
        """Register a new signer's public key"""
        self.signers[signer_id] = {
            "public_key": public_key,
            "registered_at": datetime.utcnow().isoformat(),
            "valid_until": valid_until or "2099-12-31",
            "status": "ACTIVE"
        }
        return True

    def is_signer_valid(self, signer_id: str) -> bool:
        """Check if signer's key is still valid"""
        if signer_id not in self.signers:
            return False

        signer_record = self.signers[signer_id]
        
        # Check expiration
        valid_until = signer_record.get("valid_until")
        if valid_until:
            expires_dt = datetime.fromisoformat(valid_until)
            if datetime.utcnow() > expires_dt:
                return False

        return signer_record.get("status") == "ACTIVE"

    def get_public_key(self, signer_id: str) -> Optional[str]:
        """Retrieve signer's public key"""
        if not self.is_signer_valid(signer_id):
            return None

        return self.signers[signer_id].get("public_key")

    def revoke_signer(self, signer_id: str) -> bool:
        """Revoke a signer's key (for compromised or removed members)"""
        if signer_id in self.signers:
            self.signers[signer_id]["status"] = "REVOKED"
            self.signers[signer_id]["revoked_at"] = datetime.utcnow().isoformat()
            return True
        return False

# ============================================================================
# INTEGRATION EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example: Initialize kernel
    print("=== Master_Brain Cryptographic Kernel ===\n")

    # Mock axioms and core patterns
    axioms = {
        "axioms": [
            {
                "id": "A1",
                "statement": "Truth emerges only from structured opposition",
                "introduction_version": "1.0"
            },
            {
                "id": "A2",
                "statement": "Decisions require evidence grounding",
                "introduction_version": "1.0"
            }
        ]
    }

    core_patterns = {
        "P001": {"name": "Dyadic Synthesis", "logic": "..."},
        "P002": {"name": "Quality Gradient", "logic": "..."}
    }

    # Sign kernel
    secret_key = "SUPER_SECRET_KEY_CHANGE_ME_IN_PRODUCTION_12345"
    signer = KernelSigner(secret_key)
    kernel_sig_file = signer.create_kernel_sig_file(axioms, core_patterns)

    # Verify kernel
    print("\n=== Verification ===\n")
    verifier = KernelVerifier(secret_key)
    is_valid, message = verifier.verify_kernel_from_file(axioms, core_patterns)
    print(f"Kernel valid: {is_valid}")
    print(f"Message: {message}")

    # Sign a Gnosis block
    print("\n=== Gnosis Block Signing ===\n")
    gnosis_signer = GnosisBlockSigner("alice", "alice_private_key_secret")
    
    block = {
        "id": "block_001",
        "pattern_ids": ["P077", "P080"],
        "input_data": {"decision": "Deploy Switzerland Model"},
        "output_analysis": {"recommendation": "Proceed with caution"},
        "outcome": None,
        "timestamp": datetime.utcnow().isoformat(),
        "quality_score": 6
    }

    signed_block = gnosis_signer.sign_and_record(block)
    print(f"Signed block: {json.dumps(signed_block, indent=2)}")

    # Verify
    print("\n=== Gnosis Block Verification ===\n")
    block_verifier = GnosisBlockVerifier()
    is_valid = block_verifier.verify_block(signed_block, "alice_private_key_secret", "alice")
    print(f"Block signature valid: {is_valid}")
