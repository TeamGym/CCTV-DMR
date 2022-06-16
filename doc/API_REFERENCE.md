CCTV API REFERENCE
==================

GET /cctv/info/:cam_id
---------------
데이터베이스에서 CCTV 카메라의 정보를 얻습니다.

### Request (Path Parameters)
- `cam_id`: `number` - CCTV 카메라의 id.

### Response (JSON)
- `cam_id`: `number` - CCTV 카메라의 id.
- `location`: `string` - CCTV가 설치되어있는 위치.
- `live_video_url`: `string` - CCTV의 실시간 영상을 스트리밍하는 RTSP URL.

GET /cctv/cam/info/:cam_id
--------------
CCTV 카메라에서 영상을 보내기 위한 정보를 얻습니다.
이때 클라이언트가 CCTV 카메라임을 증명하는 과정(e.g. authentication)이 필요하지만,
현재 버전에서는 생략합니다.

### Request (Path Parameters)
- `cam_id`: `number` - CCTV 카메라의 id.

### Response (JSON)
- `cam_id`: `number` - CCTV 카메라의 id.
- `rtsp_url`: `string` - 영상을 보내기 위한 RTSP URL.

POST /cctv/cam/register
--------------
CCTV 카메라의 정보를 등록합니다.
프로토타입에서만 존재하는 기능입니다.

### Request (JSON)
- `cam_id`: `number` - CCTV 카메라의 id.
- `location`: `string` - CCTV가 설치되어있는 위치.

### Response (JSON)
- `cam_id`: `number` - CCTV 카메라의 id, 정상적으로 등록되었을 경우 등록된 id가 표시됨.
