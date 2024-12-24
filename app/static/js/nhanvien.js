function add_to_gio_sach(id, name, price){
    let url = new URL(window.location.href);
    fetch("/api/sach/",{
        method: "post",
        body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price
        }),
        headers:{
            'Content-Type': 'application/json'
        }
    }).then(function(res){
        return res.json();
    }).then(function(data){
        window.location.href = url;
    });
}

function update_gio_sach(id, obj){
    obj.disabled = true;
    fetch(`/api/giosach/${id}`,{
        method: "put",
        body: JSON.stringify({
            "quantity": obj.value
        }),
        headers:{
            'Content-Type': 'application/json'
        }
    }).then(function(res){
        return res.json();
    }).then(function(data){
        obj.disabled = false;
        let carts = document.getElementByClassName("cart-counter");
        for(let d of carts)
            d.innerText = data.total_quantity;
        let amounts = document.getElementByClassName("cart-amount");
        for(d of amounts)
            d.innerText = data.total_amount.toLocaleString("en");
        let tien = document.getElementById("tien");
        let tiendu = document.getElementById("tiendu");
        tien.value = ""
        tiendu.value =""
    });
}


function delete_gio_sach(id, obj){
    if(confirm("Ban chac chan muon xoa??") == true){
        obj.disabled = true;
        fetch(`/api/giosach/${id}`,{
            method: "delete"
        }).then(function(res){
            return res.json();
        }).then(function(data){
            obj.disabled = false;
            let carts = document.getElementByClassName("cart-counter");
            for(let d of carts)
                d.innerText = data.total_quantity;
            let amounts = document.getElementByClassName("cart-amount");
            for(let d of amounts)
                d.innerText = data.total_amount.toLocaleString("en")

            let t = document.getElementById(`product${id}`);
            t.style.display = "none";
            let tien = document.getElementById("tien")
            let tiendu = document.getElementById("tiendu")
            tien.value = "";
            tiendu.value = "";
        });
    }
}


function tinh_tien_du(){
    let tien = document.getElementById("tien")
    let tiendu = document.getElementById("tiendu")
    let tongtien = document.getElementById("tong_tien").innerText;
    tongtien = tongtien.replace(/,/g,'');
    tongtien = parseFloat(tien.value);
    if(tien<tongtien){
        alert("So tien ban nhap khong hop le!!");
    }
    else{
        tiendu.value = tien- tongtien
    }
}


function lap_hoa_don(){
    if(confirm("Ban chac chan mua hang??")==true){
        let form = document.getElementById("form-thanh-toan");
        let tien = document.getElementById("tien")
        let tiendu = document.getElementById("tiendu")
        let tongtien = document.getElementById("tong_tien").innerText;
        tongtien = tongtien.replace(/,/g,'');
        tongtien = parseFloat(tien.value);
        tien = parseFloat(tien.value);
        if(tiendu.value >= 0 && (tien-tongtien)>=0){
            form.submit();
        }
        else{
            alert("Don hang khong hop le. Vui long kiem tra lai!!")
        }
    }
}