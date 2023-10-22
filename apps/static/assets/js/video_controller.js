document.addEventListener('DOMContentLoaded', function() {
    var player = videojs('my-video');
    var backButton = document.getElementById('backButton');

    player.controlBar.removeChild('SeekToLive');
        player.on('contextmenu', function(event) {
        event.preventDefault();
    });

    player.on('pause', function() {
        console.log('Il video è in pausa');
    });

    player.on('play', function() {
        console.log('Il video è in riproduzione');
    });

    player.on('click', function() {
        console.log('Hai cliccato sul video');
    });

    player.on('ended', function() {
        console.log('Il video è terminato');
    });

    player.on('timeupdate', function() {
        var currentTime = player.currentTime();
        console.log('Tempo corrente: ' + currentTime + ' secondi');
    });
    
    let controlbar =  document.querySelector(".vjs-control-bar");
    controlbar.parentNode.removeChild(controlbar);

    backButton.addEventListener('click', function() {
        var player = videojs('my-video');
        var currentTime = player.currentTime();
        player.currentTime(currentTime - 10);
    });
});

function handlePlayVideo(){};

function handlePauseVideo(){};

function handleClickVideo(){};

function handleTimeUpdate(){};

function handleVideoEnded(){};