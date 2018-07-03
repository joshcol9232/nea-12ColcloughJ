class passDisplay{
  float x;
  float y;
  int code[] = {1, 3, 5, 7};  //for testing checkCode
  int[] numbers = {};
  passDisplay(float tempX, float tempY){
    x = tempX;
    y = tempY;
  }
  
  void display(){
    fill(255);
    rect(x, y, width-100, height/6);
  }
  int addNums(int number){
    if(number == 10 && numbers.length != 0){
      numbers = shorten(numbers);
      return 100;
    }
    else{
      if (numbers.length != 4 && number != 10 && number != 11){
        numbers = append(numbers, number);
        return 100;
      }
      else{
        //println("four already added");
        return 100;
      }
    }
  }
  void displayNums(){
    if (numbers.length <= 4){
      for(int z = 0;z < numbers.length;z++){
        fill(0);
        text("*", (x+(z*100))-150, y+50);
        //println(numbers);
      }
    }
  }
  Boolean checkCode(){
    boolean correctCode = true;
    if(numbers.length == 4){
      for(int k = 0;k < numbers.length;k++){
        if(code[k] != numbers[k]){
          correctCode = false;
        }
      }
      //println("correctcode:", correctCode);
      return correctCode;
    }
    else{
      return false;
    }
  }
}
