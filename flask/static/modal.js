var modalBtn = document.querySelector('.modal-button');
var modalBg = document.querySelector('.modal-bg');
var modalClose = document.querySelector('.cancel');

modalBtn.addEventListener('click',function(){
    modalBg.classList.add('bg-active')
})
modalClose.addEventListener('click', function(){
    modalBg.classList.remove('bg-active')
})