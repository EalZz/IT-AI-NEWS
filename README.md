# Zero-Cost Daily AI News Bot

매일 아침 'AI타임스'와 'PyTorch KR' 뉴스를 크롤링하고, 무료 티어인 Google Gemini 모델을 통해 마크다운 형태로 깔끔하게 요약하여 지정된 디스코드 채널로 전송하는 **100% 완전 무료 스케줄링 봇**입니다.

## 로컬 환경 구동 방법 (테스트 목적)
1. Python 환경에서 패키지를 설치합니다: `pip install -r requirements.txt`
2. `.env` 파일을 프로젝트 루트에 생성하고 아래 환경변수를 입력합니다.
   ```
   GEMINI_API_KEY=당신의_구글_제미나이_API_키
   # 계정이 2개이거나 여러 방에 보낼 경우 쉼표(,)로 구분해서 적어주세요.
   DISCORD_WEBHOOK_URL=웹훅주소1,웹훅주소2
   ```
3. `python main.py`를 실행하여 로컬 환경에서 메시지 전송을 테스트해 봅니다.

## GitHub 자동화 환경 설정 방법 (설치형 무료 백엔드)
1. 빈 GitHub Repository를 Private로 생성합니다.
2. 현재 `d:\News_Agent` 폴더의 내용물을 생성한 GitHub Repository에 커밋하고 푸시합니다.
3. GitHub Repository 페이지 상단의 `Settings` 탭으로 이동합니다.
4. 왼쪽 메뉴에서 `Secrets and variables` -> `Actions` 를 클릭합니다.
5. **[New repository secret]** 버튼을 눌러 다음 2개의 Secret을 수동으로 등록합니다.
   - Name: `GEMINI_API_KEY` / Value: `(당신의 API Key)`
   - Name: `DISCORD_WEBHOOK_URL` / Value: `(디스코드 웹훅 주소)`
6. `.github/workflows/daily_summary.yml` 코드가 이미 포함되어 있으므로, 이제 내일부터 한국 시간으로 오전 8시에 매일마다 자동으로 스크립트가 실행되고 메시지를 발송합니다.
7. 테스트를 위해 GitHub 상단 탭 `Actions` -> `Daily Zero-Cost AI News Pipeline` -> `Run workflow` 버튼을 이용해 수동으로 즉시 구동해볼 수 있습니다.
