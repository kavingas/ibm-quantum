# from qiskit_ibm_runtime import QiskitRuntimeService

# QiskitRuntimeService.save_account(
#     token="8um0XakhcOkB-3_dkhl63wfnrhfoo0QFsU9kcwD4x3lJ", # Use the 44-character API_KEY you created and saved from the IBM Quantum Platform Home dashboard
#     instance="crn:v1:bluemix:public:quantum-computing:us-east:a/6c1a893ec8e24f6bae22c640fd310bbe:7a3fe693-588d-4220-95cf-7a542a483364::", # Optional
# )


from qiskit_ibm_runtime import QiskitRuntimeService

# Run every time you need the service
service = QiskitRuntimeService()
