const button = document.querySelector('.btn')
const form   = document.querySelector('.form')

form.addEventListener('submit', function(event) {

    var input;
    // loop each field and test if it is empty, if so then shake form to indicate it needs to be filled
    for(var i = 0; i < form.elements.length; i++) {
         input = form.elements[i].value;
         if (input == "") {
            // use this to prevent form being submitted if any unfilled fields
             event.preventDefault();
             // test if the class for the haker animation is already added to the form, if so then remove it and add it
             // back on so it will play again
            if (form.classList.contains('form--no')){
                form.classList.remove('form--no');
                // set delay of x ms so that the added classes happens after it is had enough time to remove it first
                setTimeout(function()  {form.classList.add('form--no');},10)
            } else {
                // add overwrite class to disable form load animation and trasformations so that when we come to remove
                //  the shaker animation the form does not replay its original load animation
                form.classList.add('form--overwrite');
                // associate the class for the shaker animation with the form so that it will play
                form.classList.add('form--no');
            };

            return false;
        };
    };

});
