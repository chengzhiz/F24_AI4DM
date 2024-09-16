// Teachable Machine
// The Coding Train / Daniel Shiffman
// https://thecodingtrain.com/TeachableMachine/1-teachable-machine.html
// https://editor.p5js.org/codingtrain/sketches/PoZXqbu4v

// The video

let video;
// For displaying the label
let label = "waiting...";
// The classifier
let classifier;
let modelURL = "https://teachablemachine.withgoogle.com/models/NDN6TeD5v/";

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
  tree = loadImage("assets/tree.png");
}

function setup() {
  createCanvas(400, 400);
  // Create the video
  video = createCapture(VIDEO);
  video.hide();
  // STEP 2: Start classifying
  classifyVideo();
}

// STEP 2 classify the video!
function classifyVideo() {
  classifier.classify(video, gotResults);
}

function draw() {
  background(250);

  frameRate(7);
  tint(255, 230);
  image(tree, 200, 200, 400, 400);
  text(label, width / 2, height - 16);
  imageMode(CENTER);
  console.log(flowers_n_leaves.length, follow_counter, counter);

  for (let i = 0; i < flowers_n_leaves.length - 1; i++) {
    flowers_n_leaves[i].show();
  }

  //   fading in the last flower/leaf
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

function checkLabel(label) {
  rand_x = random(30, 320);
  rand_y = random(0, 250);

  if (label == "flower" && dist(200, 159, rand_x, rand_y) <= 150) {
    r = random(20, 70);
    let f = new Flower(rand_x, rand_y, r);
    flowers_n_leaves.push(f);
    counter += 1;
    console.log("hello");
  }

  if (label == "leaf" && dist(200, 159, rand_x, rand_y) <= 150) {
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
}

function keyPressed() {
  rand_x = random(30, 320);
  rand_y = random(0, 250);

  if (key === "f" && dist(200, 159, rand_x, rand_y) <= 150) {
    r = random(20, 70);
    let f = new Flower(rand_x, rand_y, r);
    flowers_n_leaves.push(f);
    counter += 1;
  }

  if (key === "l" && dist(200, 159, rand_x, rand_y) <= 150) {
    r = random(20, 40);
    if (counter % 2) {
      let l = new Leaf(rand_x, rand_y, r);
      flowers_n_leaves.push(l);
    } else {
      let l = new Leaf_flipped(rand_x, rand_y, r);
      flowers_n_leaves.push(l);
    }
  }
  counter += 1;
}

function gotResults(error, results) {
  if (error) {
    console.error(error);
    return;
  }
  // Store the label and classify again!
  label = results[0].label;
  classifyVideo();
  // console.log(results);
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
