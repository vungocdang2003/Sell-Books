function addToCart(id, name, price, current_user_id, soluongtonkho, soluong, chuyentrang){
    if(current_user_id == ''){
        pathname = window.location.pathname
        let msg = "Ban can dang nhap!!"
        window.location.href = "/dangnhap?msg="+msg+"&next"+pathname
    }
    else{
        if(soluong==0){
            let value = document.getElementById("soluong")
            soluong = value.value
        }
        if(soluong>soluongtonkho){
            alert("So luong ton kho khong du!!")
        }
        else{
            fetch("api/cart",{
                method: "post",
                body: JSON.stringify({
                    "sanpham_id": id,
                    "tensanpham": name,
                    "gia": price,
                    "current_user_id": current_user_id,
                    "soluong": soluong
                }),
                headers:{
                    'Content-Type':'application/json'
                }
            }).then(function(res){
                return res.json();
            }).then(function(data){
                let carts = document.getElementByClassName("cart-counter");
                for(let d of carts)
                    d.innerText = data.total_quantity;
                if(chuyentrang == 'True'){
                    window.location.href = "/giohang"
                }
            });
        }
    }
}

function updateCart(id, obj){
    obj.disabled = true;
    fetch(`/api/cart/${id}`,{
        method: "put",
        body: JSON.stringify({
            "soluong": obj.value
        }),
        headers:{
            'Content-Type': 'application/json'
        }
    }).then(function(res){
        return res.json();
    }).then(function(data){
        obj.disabled = false;
        console.log(data)
        let carts = document.getElementByClassName("cart-counter");
        for(let d of carts)
            d.innerText = data.total_quantity;
        let amounts = document.getElementByClassName("cart-amount");
        for(let d of amount)
            d.innerText = data.total_amount.toLocaleString("en");
    });
}


function deleteCart(id, obj){
    if(confirm("Ban chac chan xoa??")==true){
        obj.disabled = true;
        fetch(`/api/cart/${id}`,{
            method: "delete"
        }).then(function(res){
            return res.json();
        }).then(function(data){
            obj.disabled= false;
            let carts = document.getElementByClassName("cart-counter");
            let t = document.getElementById(`product${id}`);
            if(data.total_quantity != 0){
                for(let d of carts)
                    d.innerText = data.total_quantity;
                let amounts = document.getElementByClassName("cart-amount");
                for(let d of amounts)
                    d.innerText = data.total_amount.toLocaleString("en");
                t.style.display = "none";
            }
            else{
                let thongtin = document.getElementById("form-thong-tin");
                thongtin.style.display = "none";
            }
        });
    }
}


function confirmBuy(){
    if(confirm("Ban chac chan mua hang??")== true){
        let form = document.getElementById("form-thanh-toan");
        let phone = document.getElementById("phone");
        let address = document.getElementById("address");
        if(!phone && !address){
            form.submit();
        }
        if(phone.checkValidity() && address.checkValidity()){
            form.submit();
        }
        else{
            alert("Du lieu khong hop le. Hay kiem tra lai!!")
        }
    }
}