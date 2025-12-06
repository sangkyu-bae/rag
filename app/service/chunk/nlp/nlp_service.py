from fastapi import Request
import time
class NLPService:
    def test(self, request: Request, text: str):
        kiwi = request.app.state.kiwi   # 앱에 로딩된 Kiwi 사용

        # 시작 시간
        start = time.perf_counter()
        tokens = kiwi.tokenize(text)

        result = [
            {
                "form": tok.form,
                "tag": tok.tag,
                "start": tok.start,
                "len": tok.len
            }
            for tok in tokens
        ]

      # 종료 시간
        end = time.perf_counter()

        # 경과 시간 계산
        elapsed = end - start
        print(f"[NLPService.test] 실행 시간: {elapsed:.6f}초 ({elapsed*1000:.3f}ms)")


        return result
    

    def is_broken(self, request: Request, text: str) -> bool:
        kiwi = request.app.state.kiwi   # 앱에 로딩된 Kiwi 사용
        tokens = kiwi.tokenize(text)
        pos = [t.tag for t in tokens]

        # 규칙 1: 동사 없음
        if not any(p.startswith("V") for p in pos):
            return True

        # 규칙 2: 명사 연속 3개 이상
        streak = 0
        for p in pos:
            if p.startswith("N"):
                streak += 1
                if streak >= 3:
                    return True
            else:
                streak = 0

        # 규칙 3: NN + NN + 조사 패턴
        for i in range(len(pos)-2):
            if pos[i].startswith("N") and pos[i+1].startswith("N") and pos[i+2].startswith("J"):
                return True

        # 규칙 4: 조사 이후 동사 없음
        if "JKS" in pos or "JKO" in pos:
            last_j = max(i for i, p in enumerate(pos) if p in ("JKS","JKO"))
            if not any(p.startswith("V") for p in pos[last_j:]):
                return True

        # 규칙 5: 너무 짧고 명사만 있는 문장
        if len(tokens) <= 3 and all(p.startswith("N") for p in pos):
            return True

        # 규칙 6: 특수문자 비정상 많음
        special = sum(1 for ch in text if not ch.isalnum() and ch not in " .,-()")
        if special > 3:
            return True

        return False



    # def analyze(self, text, llama_type):
    #     tokens = self.kiwi.tokenize(text)

    #     # 1) LlamaParse 타입을 우선 사용
    #     if llama_type in ["heading", "title", "list-item", "table-header"]:
    #         return { "broken": False, "type": llama_type }

    #     # 2) LlamaParse가 normal이라면 → 형태소 분석으로 품질 검사
    #     broken = self.is_broken_sentence(text, tokens, "sentence")

    #     return {
    #         "type": llama_type,
    #         "broken": broken,
    #         "tokens": [...]
    #     }