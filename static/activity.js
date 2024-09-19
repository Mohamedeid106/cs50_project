document.addEventListener('DOMContentLoaded', () => {
  let darkmodeenabled = false;
  const darkmodebtn = document.getElementById("darkmodebtn");
  let btns = document.querySelectorAll(".container-1 .content .btn");
  let titles = document.querySelectorAll(".container-2 h1");

  // btns.forEach((btn) => {
  //   btn.addEventListener("click", () => {
  //     btn.style.backgroundColor = "#d2d3db62";
  //   });
  // });
  
  darkmodebtn.addEventListener("click", () => {
    darkmodeenabled = !darkmodeenabled;
    
    if(darkmodeenabled) {
      enableDarkMode();
    } else {
      disableDarkMode();
    }
  });

  const enableDarkMode = () => {
    document.body.style.backgroundImage = 'url("../static/img_8.jpg")';
    document.querySelector(".container-1 .content .darkbtn .dark").style.opacity = "1";
    document.querySelector(".container-1 .content .darkbtn .light").style.opacity = "0.2";
    document.querySelector(".container-1").style.backgroundColor = "rgba(255,255,255,0.13)";
    document.querySelector(".container-1 .content .name").style.color = "#ffffff";
    document.querySelector(".container-1 .content .profile-edit").style.color = "#ffffff";
    btns.forEach((btn) => {
      btn.style.color = "#ffffff";  
    });
    titles.forEach((title) => {
      title.style.color = "#ffffff";
    });
  }
  
  const disableDarkMode = () => {
    document.body.style.backgroundImage = 'url("../static/img_7.jpg")';
    document.querySelector(".container-1 .content .darkbtn .light").style.opacity = "1";
    document.querySelector(".container-1 .content .darkbtn .dark").style.opacity = "0.2";
    document.querySelector(".container-1").style.backgroundColor = "#c7ccff71";
    document.querySelector(".container-1 .content .name").style.color = "#484b6a";
    document.querySelector(".container-1 .content .profile-edit").style.color = "#484b6a";
    btns.forEach((btn) => {
      btn.style.color = "#484b6a";  
    });
    titles.forEach((title) => {
      title.style.color = "#484b6a";
    });
  }

});