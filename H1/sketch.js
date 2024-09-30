// Teachable Machine
// The Coding Train / Daniel Shiffman
// https://thecodingtrain.com/TeachableMachine/1-teachable-machine.html
// https://editor.p5js.org/codingtrain/sketches/PoZXqbu4v

// The video

let video, classifier, div, textLabel;
let vec_x = 0;
let vec_y = 0;
let unit_x, unit_y;
let factor = 150;
// For displaying the label
let label = "waiting...";
// The classifier

let modelURL = "https://teachablemachine.withgoogle.com/models/NDN6TeD5v/";

let handPose;
let hands = [];

let flower, leaf, tree;
let flowers_n_leaves = [];
let counter = 0;
let follow_counter = 0;
let trans = 0;

// STEP 1: Load the model!
function preload() {
  classifier = ml5.imageClassifier(modelURL + "model.json");
  flower = loadImage("assets/flower.png");
  leaf = loadImage("assets/leaf.png");
  leaf_flipped = loadImage("assets/leaf_flipped.png");
  tree = loadImage("assets/wreath.png");

  // Options for the SpeechCommands18w model, the default probabilityThreshold is 0
  handPose = ml5.handPose({ flipped: true });
}

function setup() {
  createCanvas(400, 400);
  // Create the video
  video = createCapture(VIDEO, { flipped: true });
  video.size(400, 400);
  // video.hide();

  textLabel = createP(label);
  // textLabel.parent("modelLabel");

  classifier.classifyStart(video, gotResult);
  handPose.detectStart(video, gotHands);
}

//  for model2

function gotResult(results) {
  // The results are in an array ordered by confidence
  // Load the first label to the text variable displayed on the canvas
  predictedWord = results[0].label;
  // console.log(predictedWord)
}

function draw() {
  textLabel.html(label);

  background(250);
  frameRate(7);
  tint(255, 230);

  image(tree, 200, 200, 400, 400);
  text(label, width / 2, height - 16);
  text("let's make a cyber wreath!❀", width/2 - 70, height/2);

  imageMode(CENTER);
  // console.log(flowers_n_leaves.length, follow_counter, counter);

  if (hands.length > 0) {
    let finger = hands[0].middle_finger_mcp;
    let palm = hands[0].wrist;

    vec_x = int(finger.x - palm.x);
    vec_y = int(finger.y - palm.y);

    distance = int(sqrt(vec_x ** 2 + vec_y ** 2));

    unit_x = vec_x / distance;
    unit_y = vec_y / distance;
  }
  for (let i = 0; i < flowers_n_leaves.length - 1; i++) {
    flowers_n_leaves[i].show();
  }

  if (follow_counter < counter) {
    trans += 10;
    tint(255, trans);
    if (flowers_n_leaves.length >= 1) {
      flowers_n_leaves[flowers_n_leaves.length - 1].show();
    }

    if (trans >= 255) {
      trans = 0;
      follow_counter = counter;
    }
  }
  checkLabel(label);
}

function gotHands(results) {
  // Save the output to the hands variable
  hands = results;
}

function checkLabel(label) {
  // rand_x = int(random(30, 320) + int(unit_x * factor);
  // rand_y = int(random(0, 250)) + int(unit_y * factor);
  factor = int(random(110,130));
  rand_x = 200 + int(unit_x * factor);
  rand_y = 160 + int(unit_y * factor);
  
  console.log("rand", rand_x, rand_y, "calibrate", int(unit_x * factor), int(unit_y * factor));

  // if (dist(200, 159, rand_x, rand_y) <= 150) {
    if (label == "flower") {
      r = random(20, 80);
      let f = new Flower(rand_x, rand_y, r);
      flowers_n_leaves.push(f);
      counter += 1;
    }

    if (label == "leaf") {
      r = random(20, 40);
      if (counter % 2) {
        let l = new Leaf(rand_x, rand_y, r);
        flowers_n_leaves.push(l);
        counter += 1;
      } else {
        let l = new Leaf_flipped(rand_x, rand_y, r);
        flowers_n_leaves.push(l);
        counter += 1;
      }
    }
  // }
}

// for model1

function gotResult(results) {
  label = results[0].label;
  if (label == "flower") {
    console.log("flower");
  } else if (label == "leaf") {
    console.log("leaf");
  }
}

class Flower {
  constructor(x, y, r) {
    this.x = x;
    this.y = y;
    this.r = r;
  }

  show() {
    image(flower, this.x, this.y, this.r, this.r);
  }
}

class Leaf {
  constructor(x, y, r) {
    this.x = x;
    this.y = y;
    this.r = r;
  }

  show() {
    image(leaf, this.x, this.y, this.r, this.r);
  }
}

class Leaf_flipped {
  constructor(x, y, r) {
    this.x = x;
    this.y = y;
    this.r = r;
  }

  show() {
    image(leaf_flipped, this.x, this.y, this.r, this.r);
  }
}
