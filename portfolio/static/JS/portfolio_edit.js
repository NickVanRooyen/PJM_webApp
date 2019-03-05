//https://www.tutorialrepublic.com/codelab.php?topic=bootstrap&file=popovers

$(document).ready(function(){
    $('[data-toggle="popover"]').popover({
        placement : 'top',
        trigger:'hover'
    });
});