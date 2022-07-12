function logout() {
  $.removeCookie("campuspot_token", { path: "/" });
  console.log("로그아웃");
  alert("로그아웃 되었습니다!");
  window.location.href = "/login";
}
