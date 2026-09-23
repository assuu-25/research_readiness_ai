import asyncio
from fastapi import UploadFile
from app.main import assess

async def main():
    with open('sample_data/sample_paper.txt', 'rb') as p, open('sample_data/sample_dataset.csv', 'rb') as d:
        paper_file = UploadFile(filename="sample_paper.txt", file=p)
        dataset_file = UploadFile(filename="sample_dataset.csv", file=d)
        
        response = await assess(paper_file, dataset_file)
        import json
        print(json.dumps(json.loads(response.body), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
