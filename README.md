# 캠퍼스팟 CampuSpot

---

## 프로젝트 소개

캠퍼스팟은 대학을 중심으로 대학 주변 지역의 정보를 공유하는 커뮤니티 서비스입니다.

[캠퍼스팟 링크](http://webstudy.shop/)

## 제작 기간 & 팀원 소개

2022년 7월 11일 ~ 2022년 7월 14일

* 정찬호
* 유성원
* 조상우
* 최인영
* 최영준

## 사용 기술

`Back-end`

* Python
* Flask
* MongoDB
* Jinja2

`Front-end`

* Javascript
* JQuery

`Deploy`

* AWS EC2 (Ubuntu 18.04 LTS)

## 실행화면

![login](./img/sample.png)

[영상 링크](https://www.youtube.com/watch?v=Js1MHViLX5w)

## 주요 기능

* 커뮤니티 회원 가입, 로그인
  * JWT를 사용하여 로그인 및 로그인 유지 구현
  * 이메일(id) 중복 가입 방지

* 대학별로 존재하는 별도의 게시판
  * 주변 지역 정보 공유
  * 자유롭게 읽기 가능, 쓰기는 대학교 인증 회원만 가능

* 마이페이지
  * 별명 수정 기능
  * 내가 쓴 글만 모아보기
