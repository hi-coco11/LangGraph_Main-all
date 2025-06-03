import shutil

# ChromaDB가 저장된 디렉토리 (예: config.yaml에 정의된 값)
persist_dir = "findata/chroma_db"

# 전체 폴더 삭제 (주의: 복구 불가)
shutil.rmtree(persist_dir, ignore_errors=True)

print(f"✅ ChromaDB 디렉토리 '{persist_dir}' 삭제 완료")
