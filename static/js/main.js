function funcPasswordValidation(){
	var pass=$("#txt_Password").val();
	var confpass=$("#txt_ConfirmPass").val();
	if (pass!=confpass){
		$(".alert-danger").css("display","block");
		$(".alert-danger label").text("Password and Confirm Password doesn't match");
	} else{
		$(".alert-danger").css("display","none");
		$(".alert-danger label").text("");
	}
}

function funcValidate(id,msg){
	if ($("#"+id).val() != ""){
		$(".alert-danger").css("display","none");
		$(".alert-danger label").text("");
	} else{
		$(".alert-danger").css("display","block");
		$(".alert-danger label").text(msg);
	}
}

function funcAlertHide(){
	$(".alert-danger").css("display","none");
	$(".alert-danger label").text("");
}