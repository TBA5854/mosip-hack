import json
from datetime import datetime, timedelta
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64
import hashlib


class VCGenerator:
    """Generate W3C Verifiable Credentials"""
    
    def __init__(self, issuer_did: str = "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"):
        self.issuer_did = issuer_did
        # Generate signing key (in production, load from secure storage)
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
    
    def create_credential(self, verified_data: Dict[str, Any]) -> Dict:
        """
        Create a Verifiable Credential from verified data
        
        Args:
            verified_data: Dictionary of verified field data
            
        Returns:
            W3C Verifiable Credential as JSON-LD
        """
        # Current timestamp
        now = datetime.utcnow()
        expiry = now + timedelta(days=365)  # 1 year validity
        
        # Build credential
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/citizenship/v1"
            ],
            "id": f"urn:uuid:{self._generate_credential_id()}",
            "type": ["VerifiableCredential", "IdentityCredential"],
            "issuer": {
                "id": self.issuer_did,
                "name": "MOSIP OCR Verification System"
            },
            "issuanceDate": now.isoformat() + "Z",
            "expirationDate": expiry.isoformat() + "Z",
            "credentialSubject": {
                "id": f"did:example:{self._generate_subject_id(verified_data)}",
                **self._extract_credential_subject(verified_data)
            }
        }
        
        # Add proof (signature)
        proof = self._create_proof(credential)
        credential["proof"] = proof
        
        return credential
    
    def _extract_credential_subject(self, verified_data: Dict) -> Dict:
        """Extract and format credential subject data"""
        subject = {}
        
        # Map verified fields to credential schema
        field_mapping = {
            "name": "givenName",
            "dob": "birthDate",
            "age": "age",
            "gender": "gender",
            "email": "email",
            "phone": "telephone",
            "address": "address"
        }
        
        for ocr_field, vc_field in field_mapping.items():
            if ocr_field in verified_data:
                subject[vc_field] = verified_data[ocr_field]
        
        return subject
    
    def _create_proof(self, credential: Dict) -> Dict:
        """
        Create cryptographic proof for the credential
        
        Uses Ed25519 signature
        """
        # Create canonical form (simplified)
        credential_copy = credential.copy()
        canonical = json.dumps(credential_copy, sort_keys=True, separators=(',', ':'))
        
        # Sign
        signature = self.private_key.sign(canonical.encode('utf-8'))
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Public key for verification
        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        public_key_b64 = base64.b64encode(public_key_bytes).decode('utf-8')
        
        proof = {
            "type": "Ed25519Signature2020",
            "created": datetime.utcnow().isoformat() + "Z",
            "verificationMethod": f"{self.issuer_did}#keys-1",
            "proofPurpose": "assertionMethod",
            "proofValue": signature_b64,
            "publicKey": public_key_b64
        }
        
        return proof
    
    def _generate_credential_id(self) -> str:
        """Generate unique credential ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _generate_subject_id(self, data: Dict) -> str:
        """Generate deterministic subject ID from data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(data_str.encode())
        return hash_obj.hexdigest()[:16]
    
    def verify_credential(self, credential: Dict) -> bool:
        """
        Verify a credential's signature
        
        Returns True if valid, False otherwise
        """
        try:
            # Extract proof
            proof = credential.get("proof", {})
            signature_b64 = proof.get("proofValue")
            
            if not signature_b64:
                return False
            
            # Recreate canonical form
            credential_copy = {k: v for k, v in credential.items() if k != "proof"}
            canonical = json.dumps(credential_copy, sort_keys=True, separators=(',', ':'))
            
            # Verify signature
            signature = base64.b64decode(signature_b64)
            self.public_key.verify(signature, canonical.encode('utf-8'))
            
            return True
        except Exception:
            return False
