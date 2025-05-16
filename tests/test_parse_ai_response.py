from ai_openai import OpenAIImage2Description

def test_parse_ai_response():
    raw_content = '''
    ```json
    {
      "category_level1": "外套",
      "category_level2": "西装外套",
      "noun_features": [
        "无帽子",
        "有扣子",
        "有口袋",
        "翻领",
        "长袖"
      ],
      "adj_features": [
        "深蓝色",
        "西装材质",
        "修身",
        "正式风格",
        "中长款",
        "无图案"
      ],
      "details": "这是一件深蓝色、修身版型的西装外套，属于正式风格。外套采用西装材质，具有中长款的长度。设计上没有帽子，配有扣子和口袋，翻领经典，袖子为长袖且无任何装饰图案。",
      "prompt": "A deep blue tailored suit jacket, formal style, made of suit material, mid-length. It features no hood, buttons, pockets, a classic lapel, and long sleeves. The jacket is plain with no patterns, and presents a sophisticated and elegant look."
    }
    ```
    '''
    result = OpenAIImage2Description.parse_ai_response(raw_content)
    assert result["category_level1"] == "外套"
    assert "prompt" in result
    print("解析结果：", result) 