import os

from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService

load_dotenv()
token    = os.getenv("TOKEN")
instance = os.getenv("INSTANCE")
QiskitRuntimeService.save_account(
    token=token, # Use the 44-character API_KEY you created and saved from the IBM Quantum Platform Home dashboard
    instance=instance, # Optional
)


# Run every time you need the service
service = QiskitRuntimeService()
