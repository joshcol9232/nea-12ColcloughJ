class sqrButton {
  float x;
  float y;
  int col = 255;
  int num;
  float scale = width/3.5;
  sqrButton(float inputX, float inputY, int number, passDisplay tempDisplay) {
    x = inputX;
    y = inputY;
    num = number;
    mainDisplay = tempDisplay;
  }
  void display() {
    fill(col);
    rect(x, y, scale, scale);
    if (num == 11){
      textSize(100);
      fill(0);
      text("ENTER", x-130, y+40);
    }
    else{
      if (num == 10){
        textSize(150);
        fill(0);
        text("DEL", x-120, y+60);
      }
      else{
        textSize(150);
        fill(0);
        text(num, x-40, y+60);
      }
    }
  }
  void isPressed(){
    if ((mouseX < x+(scale/2)) && (mouseX > x-(scale/2)) && (mouseY < y+(scale/2)) && (mouseY > y-(scale/2))){
      mainDisplay.addNums(num);
      //col = 200;
      if (num == 11){
        //corr = mainDisplay.checkCode();
        if (mainDisplay.checkCode()){
          rectMode(CENTER);
          fill(#6e49c6);
          rect(width/2, height/2, width, height);
          fill(255);
          textSize(200);
          text("Correct!", width/2-400, height/2);
          frameRate(0);
        }
      }
    }
    //else{
    //  col = 255;
    //}
  }
}
