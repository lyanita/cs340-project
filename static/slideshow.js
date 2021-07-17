// display the first image immediately
setTimeout(slideshow, 0);

// then set slideshow interval
var slideshowInterval = setInterval(slideshow, 6000);

var imageSlides = document.getElementsByClassName('imageSlides');
var circles = document.getElementsByClassName('circle');
var leftArrow = document.getElementById('leftArrow');
var rightArrow = document.getElementById('rightArrow');
var imageLength = imageSlides.length;
var imageIndex = 0;

// function to hide all images
function hideImages() {
    for (var i = 0; i < imageLength; i++) {
        // use classList API to remove class
        imageSlides[i].classList.remove('visibleImage');
    }
}

// function to empty all filled circle
function emptyCircle() {
    for (var i = 0; i < imageLength; i++) {
        circles[i].classList.remove('filledCircle');
    }
}

// change current image to the next one
// empty current circle and fill the next circle
function nextImage() {
    var currentImage = imageSlides[imageIndex];
    var currentCircle = circles[imageIndex];
    // use classList API to add class
    currentImage.classList.add('visibleImage');
    emptyCircle();
    currentCircle.classList.add('filledCircle');
    imageIndex++;
}

// slideshow function
function slideshow() {
    if (imageIndex < imageLength) {
        nextImage();
    } else {
        imageIndex = 0;
        hideImages();
        nextImage();
    }
}

// left and right arrows event function
function arrowClick(event) {
    var target = event.target;

    if (target == leftArrow) {
        // reset interval when arrow is clicked
        clearInterval(slideshowInterval);
        hideImages();
        emptyCircle();

        if (imageIndex == 1) {
            imageIndex = (imageLength - 1);
            nextImage();
            slideshowInterval = setInterval(slideshow, 6000);
        } 
        else {
            imageIndex -= 2;
            nextImage();
            slideshowInterval = setInterval(slideshow, 6000);
        }
    }
    else if (target == rightArrow) {
        // reset interval when arrow is clicked
        clearInterval(slideshowInterval);
        hideImages();
        emptyCircle();

        if (imageIndex == imageLength) {
            imageIndex = 0;
            nextImage();
            slideshowInterval = setInterval(slideshow, 6000);
        } 
        else {
            nextImage();
            slideshowInterval = setInterval(slideshow, 6000);
        }
    }
}

// event listener on click
leftArrow.addEventListener('click', arrowClick);
rightArrow.addEventListener('click', arrowClick);
