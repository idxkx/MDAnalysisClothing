import fastapi.testclient
from main import app
import os

client = fastapi.testclient.TestClient(app)

TEST_IMG_PATH = "tests/test.jpg"

def test_analyze():
    with open(TEST_IMG_PATH, "rb") as f:
        img_bytes = f.read()
    response = client.post("/analyze", files={"file": (os.path.basename(TEST_IMG_PATH), img_bytes)})
    assert response.status_code == 200
    data = response.json()
    assert "color" in data and "style" in data
    print("/analyze接口返回：", data)

def test_generate():
    response = client.post("/generate", json={"description": {"color": "红色", "style": "连衣裙"}})
    assert response.status_code == 200
    data = response.json()
    assert "image_base64" in data and len(data["image_base64"]) > 10
    print("/generate接口返回图片base64长度：", len(data["image_base64"]))

def test_analyze_no_file():
    response = client.post("/analyze")
    assert response.status_code == 422  # 缺少文件参数

def test_generate_empty_desc():
    response = client.post("/generate", json={"description": ""})
    assert response.status_code == 200
    data = response.json()
    assert "image_base64" in data

def test_generate_invalid_json():
    response = client.post("/generate", data="notjson", headers={"Content-Type": "application/json"})
    assert response.status_code == 422

# def test_analyze():
#     response = client.post("/analyze", files={"file": ("test.jpg", b"fakeimgdata")})
#     assert response.status_code == 200
#     # 可根据实际返回结构补充断言

# def test_generate():
#     response = client.post("/generate", json={"description": "红色连衣裙"})
#     assert response.status_code == 200
#     # 可根据实际返回结构补充断言 