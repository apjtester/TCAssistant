class RAGSingleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGSingleton, cls).__new__(cls)
            cls._instance.rag = None  # Initialize rag variable
        return cls._instance

# Create a global instance
singleton = RAGSingleton()