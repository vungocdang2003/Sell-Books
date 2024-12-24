function confirmPassword(){
    let password = document.getElementById("password").value;
    let retypePassword = document.getElementById("retype_password").value;
    let form = document.getElementById("form-doi-mat-khau");
    if(password !== retypePassword){
        alert("Mat khau va nhap lai mat khau khong khop nhau. Hay kiem tra lai!!");
    }
    else{
        form.submit();
    }
}