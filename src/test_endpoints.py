"""
Test script to verify all Azure service endpoints are accessible and configured correctly.
"""
import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError
import requests

load_dotenv()

def test_endpoint(name, url, headers=None):
    """Test if an endpoint is accessible"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code < 500:  # Any non-server error is considered accessible
            print(f"✅ {name}: Accessible (Status: {response.status_code})")
            return True
        else:
            print(f"❌ {name}: Server error (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Connection failed - {str(e)[:100]}")
        return False

def test_azure_openai():
    """Test Azure OpenAI endpoint"""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    if not all([endpoint, api_key, api_version]):
        print("❌ Azure OpenAI: Missing configuration")
        return False
    
    # Test deployments endpoint
    url = f"{endpoint.rstrip('/')}/openai/deployments?api-version={api_version}"
    headers = {"api-key": api_key}
    return test_endpoint("Azure OpenAI", url, headers)

def test_ai_search():
    """Test AI Search endpoint"""
    endpoint = os.getenv("SEARCH_ENDPOINT")
    api_key = os.getenv("SEARCH_KEY")
    index_name = os.getenv("INDEX_NAME")
    
    if not all([endpoint, api_key, index_name]):
        print("❌ AI Search: Missing configuration")
        return False
    
    url = f"{endpoint.rstrip('/')}/indexes/{index_name}?api-version=2023-11-01"
    headers = {"api-key": api_key}
    return test_endpoint("AI Search", url, headers)

def test_cosmos_db():
    """Test Cosmos DB endpoint"""
    from azure.cosmos import CosmosClient
    
    endpoint = os.getenv("COSMOS_ENDPOINT")
    database_name = os.getenv("DATABASE_NAME")
    
    if not all([endpoint, database_name]):
        print("❌ Cosmos DB: Missing configuration")
        return False
    
    try:
        # Use DefaultAzureCredential for AAD authentication
        credential = DefaultAzureCredential()
        client = CosmosClient(endpoint, credential)
        database = client.get_database_client(database_name)
        # Try to read database properties
        database.read()
        print(f"✅ Cosmos DB: Accessible (AAD auth) and database '{database_name}' exists")
        return True
    except Exception as e:
        print(f"❌ Cosmos DB: Failed - {str(e)[:100]}")
        return False

def test_storage_account():
    """Test Storage Account endpoint"""
    from azure.storage.blob import BlobServiceClient
    
    storage_account_name = os.getenv("storage_account_name")
    container_name = os.getenv("storage_container_name")
    
    if not all([storage_account_name, container_name]):
        print("❌ Storage Account: Missing configuration")
        return False
    
    try:
        # Use DefaultAzureCredential for AAD authentication
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        credential = DefaultAzureCredential()
        blob_service = BlobServiceClient(account_url=account_url, credential=credential)
        container_client = blob_service.get_container_client(container_name)
        # Check if container exists
        container_client.get_container_properties()
        print(f"✅ Storage Account: Accessible (AAD auth) and container '{container_name}' exists")
        return True
    except Exception as e:
        print(f"❌ Storage Account: Failed - {str(e)[:100]}")
        return False

def test_application_insights():
    """Test Application Insights configuration"""
    conn_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    if not conn_string:
        print("❌ Application Insights: Missing configuration")
        return False
    
    # Parse connection string to verify format
    try:
        parts = dict(item.split("=", 1) for item in conn_string.split(";") if "=" in item)
        if "InstrumentationKey" in parts and "IngestionEndpoint" in parts:
            print(f"✅ Application Insights: Configuration valid")
            return True
        else:
            print(f"❌ Application Insights: Invalid connection string format")
            return False
    except Exception as e:
        print(f"❌ Application Insights: Failed to parse - {str(e)}")
        return False

def test_agent_ids():
    """Verify agent IDs are configured"""
    agents = {
        "Customer Loyalty": os.getenv("customer_loyalty"),
        "Inventory Agent": os.getenv("inventory_agent"),
        "Interior Designer": os.getenv("interior_designer"),
        "Cora (Shopper)": os.getenv("cora"),
        "Cart Manager": os.getenv("cart_manager")
    }
    
    all_configured = True
    for name, agent_id in agents.items():
        if agent_id and agent_id.strip():
            print(f"✅ Agent ID - {name}: Configured ({agent_id[:20]}...)")
        else:
            print(f"⚠️  Agent ID - {name}: Not configured")
            if name == "Customer Loyalty":
                all_configured = False  # Only fail if required agents missing
    
    return all_configured

def main():
    """Run all endpoint tests"""
    print("=" * 80)
    print("Testing Azure Service Endpoints")
    print("=" * 80)
    print()
    
    results = {
        "Azure OpenAI": test_azure_openai(),
        "AI Search": test_ai_search(),
        "Cosmos DB": test_cosmos_db(),
        "Storage Account": test_storage_account(),
        "Application Insights": test_application_insights(),
        "Agent IDs": test_agent_ids()
    }
    
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all(results.values()):
        print("\n🎉 All endpoints are configured correctly!")
        return 0
    else:
        print("\n⚠️  Some endpoints need attention. Review the failures above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
