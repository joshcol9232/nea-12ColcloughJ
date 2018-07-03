sqrButton b7; //create button objects
sqrButton b8;
sqrButton b9;
sqrButton b4;
sqrButton b5;
sqrButton b6;
sqrButton b1;
sqrButton b2;
sqrButton b3;
sqrButton b0;
sqrButton del;
sqrButton ent;
passDisplay mainDisplay; //Create display object

void setup() {
  fullScreen();
  orientation(PORTRAIT);
  frameRate(30);
  rectMode(CENTER);
  float rightSide = 2*(width/3)+210;
  float leftSide = (width/3)-210;
  float top = height/3;
  float mid = top+(width/3.5)+40;
  float bot = mid+(width/3.5)+40;
  float veryBot = bot+(width/3.5)+40;
  mainDisplay = new passDisplay(width/2, height/8);
  b7 = new sqrButton(leftSide, top, 7, mainDisplay);
  b8 = new sqrButton(width/2, top, 8, mainDisplay);
  b9 = new sqrButton(rightSide, top, 9, mainDisplay);
  b4 = new sqrButton(leftSide, mid, 4, mainDisplay);
  b5 = new sqrButton(width/2, mid, 5, mainDisplay);
  b6 = new sqrButton(rightSide, mid, 6, mainDisplay);
  b1 = new sqrButton(leftSide, bot, 1, mainDisplay);
  b2 = new sqrButton(width/2, bot, 2, mainDisplay);
  b3 = new sqrButton(rightSide, bot, 3, mainDisplay);
  b0 = new sqrButton(width/2, veryBot, 0, mainDisplay);
  del = new sqrButton(leftSide, veryBot, 10, mainDisplay);
  ent = new sqrButton(rightSide, veryBot, 11, mainDisplay);
}

void touchStarted() {
  int count = 0;
  //println("started");
  if (count < 1) {
    b7.isPressed();
    b8.isPressed();
    b9.isPressed();
    b4.isPressed();
    b5.isPressed();
    b6.isPressed();
    b1.isPressed();
    b2.isPressed();
    b3.isPressed();
    b0.isPressed();
    del.isPressed();
    ent.isPressed();
    count++;
  }
}

void draw() {
  background(#2484ad);

  mainDisplay.display();
  mainDisplay.displayNums();

  b7.display();
  b8.display();
  b9.display();
  b4.display();
  b5.display();
  b6.display();
  b1.display();
  b2.display();
  b3.display();
  b0.display();
  del.display();
  ent.display();
}
