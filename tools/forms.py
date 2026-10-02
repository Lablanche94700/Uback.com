# -*- coding: utf-8 -*-
"""Envoi des formulaires du site par Web3Forms : clé publique et script d'envoi, communs à tools/build_home.py
(correction, contact) et tools/build_companies.py (revendication, tour à venir, cession, source, analyse…)."""
import json

WEB3FORMS_KEY = '92486651-e759-40da-b0dc-2da4fe75bc0a'   # clé publique Web3Forms (reçue sur contact@uback.com), faite pour être dans la page
W3F_UI = {'en': dict(sending='Sending…', error='The message could not be sent. Please try again in a moment, or write to <a href="mailto:contact@uback.com">contact@uback.com</a>.'),
          'fr': dict(sending='Envoi…', error='Le message n’a pas pu être envoyé. Réessayez dans un instant, ou écrivez-nous à <a href="mailto:contact@uback.com">contact@uback.com</a>.')}

def w3f_js(lang):
    """window.ubackSend(form, subject, body) : envoi JSON à Web3Forms, page de remerciement si succès, message sinon."""
    u = W3F_UI[lang]
    return ('<script>window.ubackSend=function(f,subject,body){'
            'var b=f.querySelector("button[type=submit]"),t=b.textContent,err=f.querySelector(".form-err");'
            'if(f.botcheck&&f.botcheck.checked)return;'
            'b.disabled=true;b.textContent=' + json.dumps(u['sending']) + ';if(err)err.hidden=true;'
            'fetch("https://api.web3forms.com/submit",{method:"POST",headers:{"Content-Type":"application/json",Accept:"application/json"},'
            'body:JSON.stringify({access_key:f.access_key.value,from_name:"Uback.com",subject:subject,name:f.name.value.trim(),'
            'email:f.email.value.trim(),replyto:f.email.value.trim(),message:body,botcheck:false})})'
            '.then(function(r){return r.json();}).then(function(j){if(!j.success)throw new Error(j.message||"error");'
            'window.location.href=f.redirect.value.replace("https://uback.com","");})'
            '.catch(function(){b.disabled=false;b.textContent=t;if(!err){err=document.createElement("p");err.className="form-err";'
            'err.setAttribute("role","alert");f.appendChild(err);}err.innerHTML=' + json.dumps(u['error']) + ';err.hidden=false;});};</script>\n')
