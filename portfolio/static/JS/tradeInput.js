const button = document.querySelector('.btn')
const form   = document.querySelector('.form')

button.addEventListener('click', function() {
    // the added class "form--no" only adds the shaking animation once, so muct remove it if it exists and re add to
    //perform animation again if needed
    if (form.classList.contains('form--no')){
        // disable base class "form" animation and transformation so that when remove "form--no" the base class doesnt
        // reload animations
        form.style.transform = 'none';
        form.style.animation = 'none';
        form.classList.remove('form--no');
        // re establish base class animations so added animations still occur
        form.style.animation = ''
        // set delay of x ms so that the added classes happens after it is had enough time to remove it first
        setTimeout(function()  {form.classList.add('form--no');},2)
    } else {
        form.classList.add('form--no');
    }

});