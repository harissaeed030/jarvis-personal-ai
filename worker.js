const corsHeaders={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,POST,OPTIONS","Access-Control-Allow-Headers":"Content-Type"};
export default {
 async fetch(request,env){
  const url=new URL(request.url);
  if(request.method==="OPTIONS")return new Response(null,{headers:corsHeaders});
  if(url.pathname==="/api/health")return Response.json({status:"ok",service:"JARVIS API",configured:Boolean(env.GEMINI_API_KEY)},{headers:corsHeaders});
  if(url.pathname!=="/api/chat"||request.method!=="POST")return Response.json({error:"Not found"},{status:404,headers:corsHeaders});
  if(!env.GEMINI_API_KEY)return Response.json({error:"AI provider is not configured. Add GEMINI_API_KEY as a Worker secret."},{status:503,headers:corsHeaders});
  try{
   const body=await request.json();
   if(typeof body.message!=="string"||!body.message.trim())return Response.json({error:"Message is required."},{status:400,headers:corsHeaders});
   if(body.message.length>12000)return Response.json({error:"Message is too long (12,000 character limit)."},{status:413,headers:corsHeaders});
   const upstream=await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key="+encodeURIComponent(env.GEMINI_API_KEY),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({systemInstruction:{parts:[{text:"You are JARVIS, a helpful personal AI assistant. Reply naturally in the language the user uses, including Roman Urdu, Urdu, and English. Be accurate, clear, and honest about limitations."}]},contents:[{role:"user",parts:[{text:body.message}]}],generationConfig:{temperature:0.7,maxOutputTokens:2048}})});
   const data=await upstream.json();
   if(!upstream.ok)return Response.json({error:data.error?.message||"AI provider request failed."},{status:502,headers:corsHeaders});
   const reply=data.candidates?.[0]?.content?.parts?.map(p=>p.text||"").join("")||"I could not generate a response.";
   return Response.json({reply},{headers:corsHeaders});
  }catch(e){return Response.json({error:"Invalid request or upstream service unavailable."},{status:500,headers:corsHeaders})}
 }
};