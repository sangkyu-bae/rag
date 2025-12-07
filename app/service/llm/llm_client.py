logger = logging.getLogger(__name__)

class LlmClient:
    """
    범용 LLM 연동 클래스
    - OpenAI / Azure OpenAI / OpenAI 호환 모델 모두 지원
    - 메시지 기반 호출
    - JSON 응답 강제 옵션
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        timeout: int = 30,
    ):
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", None)
        if not self.api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다. OPENAI_API_KEY 환경 변수를 설정해주세요.")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.timeout = timeout
    
    # --------------------------
    # Retry 데코레이터 (네트워크 오류 방어)
    # --------------------------
    @backoff.on_exception(
        backoff.expo,
        (Exception,),
        max_tries=3,
        jitter=backoff.full_jitter
    )
    def _chat_completion(self, messages: List[Dict[str, Any]], **options):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            timeout=self.timeout,
            **options
        )

    # --------------------------
    # 일반 LLM 호출
    # --------------------------
    def ask(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        일반 텍스트 응답
        """
        logger.info("[LLM] request -> %s", user_prompt[:100])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        result = response.choices[0].message["content"]
        return result

    # --------------------------
    # JSON-only LLM 호출 (폼 분류 등에서 필수)
    # --------------------------
    def ask_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        LLM 응답을 JSON 형식으로 강제하고 파싱해서 반환.
        JSON이 아닐 경우 자동 재시도.
        """
        logger.info("[LLM JSON] request -> %s", user_prompt[:100])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(
            messages,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message["content"]
        logger.debug("[LLM JSON] raw response -> %s", raw)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error("LLM JSON decode error: %s", raw)
            raise ValueError("LLM JSON 응답 파싱 실패")