document.addEventListener('DOMContentLoaded', function() {
    var player = videojs('my-video');
    var isPlaying = false;

    var backButton = document.getElementById('backButton');
    var playButton = document.getElementById('playButton');
    var tempoTrascorsoElement = document.getElementById('tempoTrascorso');
    var tempoTotaleElement = document.getElementById('tempoTotale');

    player.controlBar.removeChild('SeekToLive');
        player.on('contextmenu', function(event) {
        event.preventDefault();
    });

    player.on('pause', function() {
        console.log('Il video è in pausa');
        isPlaying = false;
    });

    player.on('play', function() {
        if(!isStarted){
            handlePlayVideo();
        }
        if(!lastVisualDateSaved){
            saveLastVisualDate();
        }
        isPlaying = true;
    });

    player.on('click', function() {
        console.log('Hai cliccato sul video');
    });

    player.on('ended', function() {
        if(!isCompleted){
            handleVideoEnded();
        }
    });

    player.on('timeupdate', function() {
        var currentTime = player.currentTime();
        tempoTrascorsoElement.textContent = formatTime(currentTime);
        if (parseInt(currentTime) > 0 && parseInt(currentTime) % 30 == 0 && currentTime % 1 > 0.70){
            handleTimeUpdate(parseInt(currentTime));
        }
    });

    player.on('loadedmetadata', function() {
        tempoTotaleElement.textContent = formatTime(player.duration());
        if (!videoDuration || videoDuration == 'None' || videoDuration == ''){
            saveVideoDuration(parseInt(player.duration()));
        }
    });

    
    let controlbar =  document.querySelector(".vjs-control-bar");
    controlbar.parentNode.removeChild(controlbar);

    backButton.addEventListener('click', function() {
        var player = videojs('my-video');
        var currentTime = player.currentTime();
        player.currentTime(currentTime - 10);
    });

    playButton.addEventListener('click', function() {
        var player = videojs('my-video');
        isPlaying? player.pause() : player.play();
    });

});

function formatTime(seconds) {
    var minutes = Math.floor(seconds / 60);
    var seconds = Math.floor(seconds % 60);
    return pad(minutes) + ':' + pad(seconds);
}

function pad(num) {
    return (num < 10) ? '0' + num : num;
}


function handlePlayVideo(){
    
    // salvo l'informazioche che l'utente ha iniziato a guardare il video
    $.ajax({
        url: `/utente/videocorso/${VIDEO_ID}/`, 
        type: 'POST',
        data: {'csrfmiddlewaretoken': csrftoken, 'is_started': true}, 
        success: function(response) {
          console.log("Video iniziato.");
          isStarted = true;
        },
        error: function(xhr, status, error) {
          // gestisce gli errori
          console.log(xhr.responseText);
        }
    });
};

function handlePauseVideo(){};

function handleClickVideo(){};

function handleTimeUpdate(watched_seconds){
    $.ajax({
        url: `/utente/videocorso/${VIDEO_ID}/`, 
        type: 'POST',
        data: {'csrfmiddlewaretoken': csrftoken, 'watched_seconds': watched_seconds}, 
        success: function(response) {
          console.log("Aggiornati secondi visualizzati.");
        },
        error: function(xhr, status, error) {
          // gestisce gli errori
          console.log(xhr.responseText);
        }
    });
};

function handleVideoEnded(){
    // salvo l'informazioche che l'utente ha iniziato a guardare il video
    $.ajax({
        url: `/utente/videocorso/${VIDEO_ID}/`, 
        type: 'POST',
        data: {'csrfmiddlewaretoken': csrftoken, 'is_completed': true}, 
        success: function(response) {
          console.log("Video completato.");
          isCompleted = true;
        },
        error: function(xhr, status, error) {
          // gestisce gli errori
          console.log(xhr.responseText);
        }
    });
}

function saveVideoDuration(video_duration){
    // salvo l'informazioche che l'utente ha iniziato a guardare il video
    $.ajax({
        url: `/utente/videocorso/${VIDEO_ID}/`, 
        type: 'POST',
        data: {'csrfmiddlewaretoken': csrftoken, 'video_duration': video_duration}, 
        success: function(response) {
            console.log("Durata video aggiornata");
            videoDuration = video_duration;
        },
        error: function(xhr, status, error) {
            // gestisce gli errori
            console.log(xhr.responseText);
        }
    });
}

function saveLastVisualDate(){
    // salvo l'informazioche che l'utente ha iniziato a guardare il video
    $.ajax({
        url: `/utente/videocorso/${VIDEO_ID}/`, 
        type: 'POST',
        data: {'csrfmiddlewaretoken': csrftoken, 'update_visual_date': true}, 
        success: function(response) {
            console.log("Data ultima visual aggiornata");
            lastVisualDateSaved = true;
        },
        error: function(xhr, status, error) {
            // gestisce gli errori
            console.log(xhr.responseText);
        }
    });
};