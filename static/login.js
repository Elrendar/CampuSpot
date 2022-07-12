// {% if msg %}
//     alert("{{ msg }}")
// {% endif %}

// 로그인 버튼
function sign_in() {
  // 브라우저 상에서 입력된 값을 받아온다
  const email = $("#input-email").val();
  const password = $("#input-password").val();

  // 이메일 입력 체크
  if (email === "") {
    // 입력칸 아래에 도움 메시지 출력
    $("#help-email-login").text("이메일을 입력해주세요.");
    // 이메일 입력 칸으로 포커스 옮김
    $("#input-email").focus();
    return;
  }
  if (!is_email(email)) {
    $("#help-email-login")
      .text("올바른 이메일 주소가 아닙니다.")
      .removeClass("is-safe")
      .addClass("is-danger");
    $("#input-email").focus();
    return;
  } else {
    // 도움 메시지 삭제
    $("#help-email-login").text("");
  }
  // 비밀번호 입력 체크
  if (password === "") {
    $("#help-password-login").text("비밀번호를 입력해주세요.");
    $("#input-password").focus();
    return;
  } else {
    $("#help-password-login").text("");
  }
  // 입력된 이메일과 비밀번호를 서버로 전송
  $.ajax({
    type: "POST",
    url: "/sign_in",
    data: {
      email_give: email,
      password_give: password,
    },
    success: function (response) {
      // 입력한 계정이 db에 존재하면
      if (response["result"] === "success") {
        // 받아온 jwt를 사용해서 세션 쿠키 생성 (브라우저 종료시 사라짐)
        $.cookie("campuspot_token", response["token"], { path: "/" });
        // 메인 페이지로
        window.location.replace("/");
      } else {
        // db에 없으면 경고 메시지
        alert(response["msg"]);
      }
    },
  });
}

// 회원 가입 버튼
function sign_up() {
  const email = $("#input-email").val();
  const password = $("#input-password").val();
  const password2 = $("#input-password2").val();

  // 도움 메시지의 상태(is-success | is-danger)를 통해 양식에 맞는 값이 들어왔는지 체크
  if ($("#help-email").hasClass("is-danger")) {
    alert("이메일을 다시 확인해주세요.");
    return;
  } else if (!$("#help-email").hasClass("is-success")) {
    alert("이메일 중복확인을 해주세요.");
    return;
  }

  // 비밀번호 칸이 빈 칸인지 체크
  if (password === "") {
    $("#help-password")
      .text("비밀번호를 입력해주세요.")
      .removeClass("is-safe")
      .addClass("is-danger");
    $("#input-password").focus();
    return;
  } else if (!is_password(password)) {
    $("#help-password")
      .text(
        "비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 특수문자(!@#$%^&*) 사용가능 8-20자"
      )
      .removeClass("is-safe")
      .addClass("is-danger");
    $("#input-password").focus();
    return;
  } else {
    $("#help-password")
      .text("사용할 수 있는 비밀번호입니다.")
      .removeClass("is-danger")
      .addClass("is-success");
  }
  if (password2 === "") {
    $("#help-password2")
      .text("비밀번호를 입력해주세요.")
      .removeClass("is-safe")
      .addClass("is-danger");
    $("#input-password2").focus();
    return;
  } else if (password2 !== password) {
    $("#help-password2")
      .text("비밀번호가 일치하지 않습니다.")
      .removeClass("is-safe")
      .addClass("is-danger");
    $("#input-password2").focus();
    return;
  } else {
    $("#help-password2")
      .text("비밀번호가 일치합니다.")
      .removeClass("is-danger")
      .addClass("is-success");
  }

  const campus = $("#select-campus option:selected").val();
  console.log(campus);

  if (campus === "없음") {
    $("#help-campus")
      .text("소속 대학을 선택해야 합니다.")
      .removeClass("is-safe")
      .addClass("is-danger");
    $("#select-campus").focus();
    return;
  } else {
    $("#help-campus").text("");
  }

  $.ajax({
    type: "POST",
    url: "/sign_up/save",
    data: {
      email_give: email,
      password_give: password,
      campus_give: campus,
    },
    success: function (response) {
      alert("회원가입을 축하드립니다!");
      window.location.replace("/login");
    },
  });
}

function toggle_sign_up() {
  $("#sign-up-box").toggleClass("is-hidden");
  $("#div-sign-in-or-up").toggleClass("is-hidden");
  $("#btn-check-dup").toggleClass("is-hidden");
  $("#help-email").toggleClass("is-hidden");
  $("#help-password").toggleClass("is-hidden");
  $("#help-password2").toggleClass("is-hidden");
  $("#help-campus").toggleClass("is-hidden");
}

// 이메일과 비밀번호 양식 체크
function is_email(asValue) {
  // 영문과 숫자, ._-를 사용한 2~10자 내의 아이디 정규식
  // const regExp = /^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{2,10}$/;
  // 이메일 정규식
  const regExp = /^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
  return regExp.test(asValue);
}

function is_password(asValue) {
  const regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
  return regExp.test(asValue);
}

// 이메일 중복체크
function check_dup() {
  let email = $("#input-email").val();
  console.log(email);
  $("#help-email").hasClass("is-danger");

  // 이메일 양식 체크
  if (email == "") {
    $("#help-email")
      .text("이메일을 입력해주세요.")
      .removeClass("is-safe")
      .addClass("is-danger");
    $("#input-email").focus();
    return;
  }
  if (!is_email(email)) {
    $("#help-email")
      .text("올바른 이메일 주소가 아닙니다.")
      .removeClass("is-safe")
      .addClass("is-danger");
    $("#input-email").focus();
    return;
  }

  $("#help-email").text("");

  // db에 이메일이 존재하는지 체크
  $.ajax({
    type: "POST",
    url: "/sign_up/check_dup",
    data: {
      email_give: email,
    },
    success: function (response) {
      // db에 있으면 메시지 출력
      if (response["exists"]) {
        $("#help-email")
          .text("이미 가입된 이메일입니다.")
          .removeClass("is-safe")
          .addClass("is-danger");
        $("#input-email").focus();
      } else {
        $("#help-email")
          .text("가입할 수 있는 이메일입니다.")
          .removeClass("is-danger")
          .addClass("is-success");
      }
    },
  });
}
