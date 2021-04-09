age="JavaScript" >
function enviardados(){
  
	  
	  
	if( document.user.email.value=="" || 
		document.user.email.value.indexOf('@')==-1 || 
		document.user.email.value.indexOf('.')==-1 )
	{
		alert( "Preencha campo E-MAIL corretamente!" );
		document.user.email.focus();
		return false;
	}
	  
	if (document.user.senha.value=="")
	{
		alert( "Preencha o campo Senha!" );
		document.user.senha.focus();
		return false;
	}
	  
	
  
return true;
}