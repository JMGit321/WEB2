from django.shortcuts import render,redirect
from .models import Causa,Doacao, UserProfile, Sugestao
from django.db.models import Max
from django.template.defaulttags import register
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .form import ImageUploadForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from random import randint
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import pyboleto
from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.data import BoletoData
from pyboleto.pdf import BoletoPDF
from datetime import date

#importações para converter em PDF
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa


# Create your views here.


def home(request):
    text_c = Causa.objects.all()
    users_cont = User.objects.all()
    cont_u = 0
    for u in users_cont:
        cont_u+=1
    users_cont = {'users_cont':cont_u}
    print(users_cont)
    if text_c:
        calculo = 0
        calculo2 = 0
        valor = Causa.objects.filter(ativo=True).aggregate(Max('meta'))
        valor = valor['meta__max']

        causa = Causa.objects.filter(ativo=True, meta=valor).order_by('-data')
        causa_dest = {}
        for c in causa:
            causa_dest[c] = c
            break
        for c in causa:
            calculo = {'calc':int(c.recebido/c.meta*100)}
        causas_all = Causa.objects.filter(ativo=True)
        calculo2 = {}
        for c in causas_all:
             calculo2[c] = int(c.recebido/c.meta*100)
        causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
        cont = 0
        evento = {}
        for c in causas_all2:
            evento[c] = c
            cont+=1
            if(cont==3):
                break
        return render(request,'index.html',{'cont_u':users_cont,'causa':causa_dest,'calc':calculo,'causas':causas_all,'calc2':calculo2,'evento':evento})
    return render(request,'index.html',{'cont_u':users_cont})

def login_user(request):
    return render(request, 'login.html')


@csrf_protect
def submit_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request,'Usuário ou Senha inválidos. Por favor tentar novamente.')
    return redirect('/login')

@login_required(login_url='/login')
def profile(request, id):
    user = User.objects.get(id=id)
    causas = Causa.objects.filter(usuario=user.id)
    doacoes = Doacao.objects.filter(usuario=user.id)
    causas_rodape = Causa.objects.all()
    return render(request, 'profile.html', {'user':user, 'causas':causas, 'doacoes':doacoes, 'evento':causas_rodape})

def my_suggestions(request, id):
    user = User.objects.get(id=id)
    sugestoes = Sugestao.objects.filter(usuario=user.id)
    return render(request, 'my-suggestions.html', {'sugestoes':sugestoes})

def completed_causes(request):
    causas = Causa.objects.filter(ativo=False)
    return render(request, 'completed-cause.html', {'causas':causas})

def forgot_pass(request):
    return render(request, 'forgot-password.html')

def reset_pass(request):
    username = request.POST.get('username')
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            user = None;
        if user:
            html_content = render_to_string('email-pass.html', {'user':user})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives('Redefinir Senha', text_content, settings.EMAIL_HOST_USER, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            messages.error(request, "Este usuário não existe!")
    else:
        messages.error(request, "Não deixe o campo nulo!")

    return render(request, 'forgot-password.html')


def confirm_reset(request, id):
    user = User.objects.get(id=id)
    new_pass = request.POST.get('new_pass')
    if new_pass:
        if not new_pass.isdigit() and not user.username in new_pass:
            user.set_password(new_pass)
            user.save()
            logout(request)
            return redirect('/')
        else:
            messages.error(request,'A senha não pode ter apenas números e não pode ser semelhantes a outras informações suas!!!')
    return render(request, 'confirm_reset.html', {'user':user})


@csrf_protect
def logout_user(request):
    logout(request)
    return redirect('/login')

@login_required(login_url='/login')
def delete_user(request, id):
    usuario = User.objects.get(id=id)
    if usuario == request.user:
        usuario.delete()

    return redirect('/login')


def register_user(request):

    if request.POST:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        r_password = request.POST.get('r_password')
        user_id = request.POST.get('user-id')
        photo_upload_form = request.FILES.get('image')
        user = request.user
        context = {
            "photo_upload_form": photo_upload_form
        }

        if user_id:
            usuario = User.objects.get(id=user_id)
            if usuario == user:
                usuario.username = username
                usuario.email = email
                usuario.save()
                if photo_upload_form:
                    prof = UserProfile.objects.get(user=user)
                    prof.image = photo_upload_form
                    prof.save()
                
                url = '/profile/{}/'.format(user_id)
                return redirect(url)
            return render(request, 'register.html', {'usuario':usuario})

        elif username and email and password and r_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Este nome de usuário já existe!!!')
                return redirect('/register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Este email já existe!!!')
                return redirect('/register')

            elif password != r_password:
                messages.error(request, 'As senhas não coincidem!!!')
                redirect('/register')
            elif password.isdigit() and user.username in password:
                messages.error(request,'A senha não pode ter apenas números e não pode ser semelhantes a outras informações suas!!!')
            else:
                new_user = User.objects.create_user(username = username, email = email, password = password)
                upload_pic(request, photo_upload_form, username=username)
                return redirect('/login')
        else:
            messages.error(request, 'Não deixe os campos nulos!!!')
    return render(request, 'register.html')


def upload_pic(request, image, username):
    if request.method == 'POST':
        User = get_user_model()
        user = User.objects.get(username=username)
        if image:
            new_user_profile = UserProfile.objects.create(user=user, image=image)
            new_user_profile.save()
        else:
            new_user_profile = UserProfile.objects.create(user=user)
            new_user_profile.save()



@login_required(login_url='/login')
def register_cause(request):

    cause_id = request.GET.get('id')
    if cause_id:
        causa = Causa.objects.get(id=cause_id)
        if causa.usuario == request.user:
            return render(request, 'register-cause.html', {'causa':causa})
    return render(request, 'register-cause.html')

@login_required(login_url='/login')
def set_cause(request):
    titulo = request.POST.get('titulo')
    meta = request.POST.get('meta')
    descricao = request.POST.get('descricao')
    fins = request.POST.get('fins')
    info = request.POST.get('info')
    foto = request.FILES.get('foto')
    user = request.user
    causa_id = request.POST.get('causa-id')
    id_causa = None
    if causa_id:
        causa = Causa.objects.get(id=causa_id)
        if user == causa.usuario:
            causa.titulo = titulo
            causa.meta = meta
            causa.descricao = descricao
            causa.fins = fins
            causa.info = info
            if foto:
                causa.foto = foto
            id_causa = causa_id
            causa.save()
            url = '/galeria/{}/'.format(id_causa)
    else:
        url = '/causas/register/'
        if titulo and meta and descricao and fins and info and foto:
            new_cause = Causa.objects.create(titulo=titulo, meta=meta, descricao=descricao, fins=fins, info=info, foto=foto, usuario=user)
            id_causa = new_cause.id
            url = '/galeria/{}/'.format(id_causa)
        else:
            messages.error(request, 'Não deixe campos nulos')
    return redirect(url)
    
@login_required(login_url='/login')
def delete_cause(request, id):
    cause = Causa.objects.get(id=id)
    if cause.usuario == request.user:
        cause.delete()

    return redirect('/')

def galeria(request):
    causa = Causa.objects.filter(ativo=True)
    if causa:
        causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
        cont = 0
        evento = {}
        for c in causas_all2:
            evento[c] = c
            cont+=1
            if(cont==3):
                break
        return render(request,'portfolio.html',{'causa':causa,'evento':evento})
    return render(request,'portfolio.html',{'causa':causa})


def single(request,id):
    causa = Causa.objects.get(id=id)
    calculo = {'calc':int(causa.recebido/causa.meta*100)}
    causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
    cont = 0
    evento = {}
    for c in causas_all2:
        evento[c] = c
        cont+=1
        if(cont==3):
            break

    return render(request,'single-causes.html',{'causa':causa,'calc':calculo,'evento':evento})

def postagens(request):
    string = request.GET.get('search')

    if string:
        causa = Causa.objects.filter(ativo=True,titulo__icontains=string).order_by('-data')
    else:
        causa = Causa.objects.filter(ativo=True).order_by('-data')# o sinal de menos inverte a ordem
    if causa:
        causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
        cont = 0
        evento = {}
        for c in causas_all2:
            evento[c] = c
            cont+=1
            if(cont==3):
                break
        page = request.GET.get('page', 1)
        paginator = Paginator(causa,5)
        teste_causa = Causa.objects.all()
        users = paginator.page(page)


        valor = Causa.objects.filter(ativo=True).aggregate(Max('meta'))
        valor = valor['meta__max']
        causa2 = Causa.objects.filter(ativo=True, meta=valor)
        for c in causa2:
            calculo = {'calc':int(c.recebido/c.meta*100)}
        return render(request,'news.html',{'users':users,'calc':calculo,'causa2':causa2,'evento':evento})
    else:
        causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
        cont = 0
        evento = {}
        for c in causas_all2:
            evento[c] = c
            cont+=1
            if(cont==3):
                break
    return render(request,'news.html',{'evento':evento})




def sobre(request):
    causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
    cont = 0
    evento = {}
    for c in causas_all2:
        evento[c] = c
        cont+=1
        if(cont==3):
            break

    return render(request,"about.html",{'evento':evento})



def contato(request):
    user = request.user
    causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
    cont = 0
    evento = {}
    for c in causas_all2:
        evento[c] = c
        cont+=1
        if(cont==3):
            break
    return render(request,'contact.html',{'evento':evento, 'user':user})
    
@login_required(login_url='/login')
def send_msg(request):
    msg = request.POST.get('msg')
    user_id = request.POST.get('user-id')
    user = User.objects.get(id=user_id)
    print(user.email)
    send_msg = EmailMultiAlternatives('Contato', msg, user.email, [settings.EMAIL_HOST_USER])
    send_msg.send()
    messages.success(request, 'Sua sugestão foi enviada, obrigado!')
    return redirect('/contato')

def sugestao(request):

    causas_all2 = Causa.objects.filter(ativo=True).order_by('-data')
    cont = 0
    evento = {}
    for c in causas_all2:
        evento[c] = c
        cont+=1
        if(cont==3):
            break
    return render(request, 'suggestion.html', {'evento':evento})

@login_required(login_url='/login')
def send_suggestion(request):
    donatario = request.POST.get('donatario')
    meta = request.POST.get('meta')
    texto = request.POST.get('texto')
    usuario = request.user

    if donatario and meta and texto:
        sugestao = Sugestao.objects.create(donatario=donatario, meta=meta, texto=texto, usuario=usuario)
        messages.success(request, 'Sua sugestão foi enviada! Aguarde a validação da mesma no seu perfil, obrigado.')
    else:
        messages.error(request, 'Não deixe campos nulos')
    return redirect('/sugestao')

def validate_suggestion(request):

    sugestoes = Sugestao.objects.filter(status=0)

    causas_all2 = Causa.objects.filter(ativo=True).order_by('-data')
    cont = 0
    evento = {}
    for c in causas_all2:
        evento[c] = c
        cont+=1
        if(cont==3):
            break
    return render(request, 'validate-suggestion.html', {'evento':evento, 'sugestoes':sugestoes})

def confirm_suggestion(request, id):
    sugestao = Sugestao.objects.get(id=id)
    sugestao.status = 1
    sugestao.save()
    return redirect('/sugestoes')

def reject_suggestion(request, id):
    sugestao = Sugestao.objects.get(id=id)
    sugestao.status = 2
    sugestao.save()
    return redirect('/sugestoes')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def causas(request):

    string = request.GET.get('search')

    if string:
        causas_all = Causa.objects.filter(ativo=True,titulo__icontains=string).order_by('-data')
    else:
        causas_all = Causa.objects.filter(ativo=True).order_by('-data')

    if causas_all:
        valor = Causa.objects.filter(ativo=True).aggregate(Max('meta'))
        valor = valor['meta__max']

        causa = Causa.objects.filter(ativo=True, meta=valor).order_by('-data')
        causa_dest = {}
        for c in causa:
            causa_dest[c] = c
            break
        for c in causa:

            calculo = {'calc':int(c.recebido/c.meta*100)}

        calculo2 = {}

        for c in causas_all:
             calculo2[c] = int(c.recebido/c.meta*100)
        causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
        cont = 0
        evento = {}
        for c in causas_all2:
            evento[c] = c
            cont+=1
            if(cont==3):
                break



        print(causas_all)
        return render(request,'causes.html',{'evento':evento,'causa':causa_dest,'calc':calculo,'causas':causas_all,'calc2':calculo2})
    return render(request,'causes.html')


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None




def generate_boleto(user, valor, nome, cpf, endereco, cep):
    boleto = BoletoBB(7,2)
    boleto.nosso_numero = '1'
    boleto.numero_documento = '1231231'
    boleto.convenio = '5555555'
    boleto.especie_documento = 'DM'

    boleto.carteira = '20'
    boleto.cedente = 'The Charity'
    boleto.cedente_documento = '123456789'
    boleto.cedente_endereco = 'R. Cicero Duarte, nº905 - Junco'
    boleto.agencia_cedente = '12345'
    boleto.conta_cedente = '4444444'

    data_hj = date.today()
    boleto.data_vencimento = date.fromordinal(data_hj.toordinal()+5)
    boleto.data_documento = data_hj
    boleto.data_processamento = data_hj

    boleto.valor_documento = valor

    boleto.sacado_nome = nome
    boleto.sacado_documento = cpf
    boleto.sacado_cidade = 'Picos'
    boleto.sacado_uf = 'Piaui'
    boleto.sacado_endereco = endereco
    boleto.sacado_cep = cep

    boleto.valor = valor
    boleto.valor_documento = valor

    boleto.quantidade = '1'

    boleto.barcode
    boleto.linha_digitavel

    return boleto
    
   


@login_required(login_url='/login')
def donate_cause(request, id):
   
    valor = request.POST.get('nota')
    if valor:
        causa = Causa.objects.get(id=id)
        comp = float(causa.meta) - float(causa.recebido) 
        if float(valor) <= comp:
            usuario = request.user
            user = request.user
            nome = request.POST.get('nome')
            cpf = request.POST.get('cpf')
            endereco = request.POST.get('endereco')
            cep = request.POST.get('cep')

            if nome and cpf and endereco and cep:
                boleto = generate_boleto(user, valor, nome, cpf, endereco, cep)
                context = {"boleto":boleto}
                pdf = render_to_pdf('boleto.html', context)
                doacao = Doacao.objects.create(valor=valor, usuario=usuario, causa=causa)
                return HttpResponse(pdf, content_type='application/pdf')
            else:
                messages.error(request, 'Não deixe os campos nulos!')
        else:
            messages.error(request, 'O valor informado excede a meta!!!')
    else:
        messages.error(request, 'Informe o valor para a doação!!!')


    url = '/galeria/{}/'.format(id)
    return redirect(url)

def donates(request):
    causas = Causa.objects.all()
    doacoes = Doacao.objects.filter(pago=False)
    valor = 0
    valores_dict = {}
    valor = 0
    for causa in causas:
        for doacao in doacoes:
          if causa.titulo == doacao.causa.titulo:
              valor += doacao.valor
        valores_dict[causa.titulo] = valor
        valor = 0
    return render(request, 'validate_donate.html', {'evento':causas, 'doacoes':doacoes})

def validate_donate(request, id):
    donate = Doacao.objects.get(id=id)
    donate.pago = 1
    donate.causa.recebido += donate.valor
    
    if donate.causa.recebido == donate.causa.meta:
        donate.causa.ativo = False
    
    donate.causa.save()
    donate.save()

    return redirect('/validar/')

def reject_donate(request, id):
    donate = Doacao.objects.get(id=id)
    donate.pago = 2
    donate.save()

    return redirect('/validar/')


def help(request):
    causa = Causa.objects.filter(ativo=True)
    if causa:
        causas_all2 =  Causa.objects.filter(ativo=True).order_by('-data')
        cont = 0
        evento = {}
        for c in causas_all2:
            evento[c] = c
            cont+=1
            if(cont==3):
                break
        return render(request,'help.html',{'evento':evento})
    return render(request, 'help.html')
