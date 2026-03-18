import re
import logging

logger = logging.getLogger("PIIMasker")

# シンプルなPII（氏名、電話番号、メール、住所等）のパターン
PII_PATTERNS = {
    "email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
    "phone": r'\d{2,4}-\d{2,4}-\d{4}',
    "credit_card": r'\d{4}-\d{4}-\d{4}-\d{4}'
}

def mask_sensitive_data(text, mask_char="*"):
    """
    テキスト内の機密情報（PII）をマスクする。
    LLMに送る前の「流出防止」フィルターとして使用。
    """
    if not isinstance(text, str):
        return text
        
    masked_text = text
    for label, pattern in PII_PATTERNS.items():
        found = re.findall(pattern, masked_text)
        for match in found:
            # 完全に隠すのではなく。種別がわかるようにマスク
            masked_text = masked_text.replace(match, f"[{label}_MASKED]")
            
    if masked_text != text:
        logger.info("Sensitive data detected and masked in outbound text.")
        
    return masked_text

def sanitize_payload(payload):
    """
    辞書形式のペイロードを再帰的にスキャンしてマスクする。
    """
    if isinstance(payload, dict):
        return {k: sanitize_payload(v) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [sanitize_payload(i) for i in payload]
    elif isinstance(payload, str):
        return mask_sensitive_data(payload)
    else:
        return payload

if __name__ == "__main__":
    test_str = "Customer email is torihikimoen@gmail.com and phone is 090-1234-5678."
    print(f"Original: {test_str}")
    print(f"Masked:   {mask_sensitive_data(test_str)}")
    
    test_dict = {
        "client": "John Doe",
        "details": "Contact at john.doe@example.com for payment 1234-5678-9012-3456"
    }
    print(f"Original Dict: {test_dict}")
    print(f"Masked Dict:   {sanitize_payload(test_dict)}")
