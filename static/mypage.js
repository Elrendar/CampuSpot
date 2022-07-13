function regenerateMyInfo() {
  $('#details').append(`<fieldset disabled>
          <div class="field">
            <label class="label">별명</label>
            <div class="control has-icons-left has-icons-right">
              <input
                  id="input-username"
                  class="input"
                  type="text"
                  placeholder="한글, 영문 2~8자"
              />
              <span class="icon is-small is-left">
              <i class="fa fa-user"></i>
            </span>
            </div>
          </div>
        </fieldset>
        <!-- 이메일 -->
        <fieldset disabled>
          <div class="field">
            <label class="label">Email</label>
            <div class="control has-icons-left">
              <input
                  id="input-email"
                  class="input"
                  type="email"
                  placeholder="이메일"
                  value="example@gmail.com"
              />
              <span class="icon is-small is-left">
                <i class="fa fa-envelope"></i>
              </span>
            </div>
            <!-- <p class="help is-danger">This email is invalid</p> -->
          </div>
        </fieldset>
        <!-- 대학 정보 받아서 표시 -->
        <fieldset disabled>
          <div class="field">
            <label class="label">소속 대학</label>
            <div class="control has-icons-left">
              <input
                  id="input-campus"
                  class="input"
                  type="text"
                  placeholder="없음"
              />
              <span class="icon is-small is-left">
                <i class="fa fa-university"></i>
              </span>
            </div>
          </div>
        </fieldset>
        <!-- 생년월일 받아서 표시 -->
        <fieldset disabled>
          <div class="field">
            <label class="label">생년월일</label>
            <div class="control has-icons-left">
              <input
                  id="input-birth"
                  class="input"
                  type="text"
                  placeholder="0000-00-00"
              />
              <span class="icon is-small is-left">
                <i class="fa fa-birthday-cake"></i>
              </span>
            </div>
          </div>
        </fieldset>
        <!-- 수정 버튼 -->
        <button class="button is-dark" onclick="saveInfo()">회원 정보 수정</button>`);
}