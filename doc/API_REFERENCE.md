CCTV API REFERENCE
==================

JSON의 매개변수는 다음과 같은 형식으로 표현됩니다:
- `<매개변수>`: `<자료형>` - 설명
이것을 JSON으로 표현하면 다음과 같습니다:
```json
{
  "<매개변수>": "<값>"
}
```
매개변수의 자료형은 JSON을 기준으로 합니다.

optional parameters의 하위항목이 아닌 매개변수는 모두 필수입니다.

POST /getinfo-cctv
---------------
데이터베이스에서 CCTV의 정보를 얻습니다.

### Request (JSON)
- `id`: `number` - CCTV의 id.

### Response (JSON)
- `id`: `number` - CCTV의 id.
- `location`: `string` - CCTV가 설치되어있는 위치.
- `live_video_url`: `string` - CCTV의 실시간 영상을 스트리밍하는 URL.
-


POST /streaminginfo-cctv
--------------
CCTV에서 영상을 보내기 위한 정보를 얻습니다.
이때 클라이언트가 CCTV임을 증명하는 과정(e.g. authentication)이 필요하지만,
현재 버전에서는 생략합니다.

### Request (JSON)
- `id`: `number` - CCTV의 id.

### Response (JSON)
- `id`: `number` - CCTV의 id.
- `url`: `string` - RTP ...
