# crud-solo

FastAPI + Jinja2로 만든 간단한 게시판입니다. DB 없이 메모리(딕셔너리)에 저장하므로 서버를 재시작하면 글이 초기화됩니다.

## 실행

```
uv sync
uv run fastapi dev
```

브라우저에서 http://127.0.0.1:8000 접속

## 기능

| 기능 | 메서드 | 경로 |
|---|---|---|
| 목록 / 검색 | GET | `/posts`, `/posts?q=검색어` |
| 작성 폼 | GET | `/posts/new` |
| 작성 | POST | `/posts/create` |
| 상세 | GET | `/posts/{id}` |
| 수정 폼 | GET | `/posts/{id}/edit` |
| 수정 | POST | `/posts/{id}/update` |
| 삭제 | POST | `/posts/{id}/delete` |

## 구조

```
main.py            라우트, 메모리 저장소
templates/
  base.html        공통 레이아웃과 스타일
  list.html        목록
  detail.html      상세
  form.html        작성/수정 공용 폼
  404.html         없는 글
```
