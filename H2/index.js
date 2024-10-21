// index.js
// A directory named "public" is available in the current directory.
// The public directory holds index.html containing HTML and Javascript.
// A browser will visit with http://localhost:3000/index.html

const express = require('express')
const port = 4000
app = express();
// allow access to the files in public
app.use(express.static('public'));

app.listen(port, () => {
  console.log(`Mouse moving app listening at http://localhost:${port}/index.html`)
})
