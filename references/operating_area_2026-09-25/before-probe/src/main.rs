mod fixture;
use fixture::*;
use rx_domain::types::*;
use rx_supervisor::{decision::*,use_assessment::*};
fn policy()->Policy { Policy { authorities:[(n("test/no-private-key"),Authority {
 issuer:n("test/authored-catalog"), public_key:rx_package::release::root::PUBLIC_KEY,
 operating_area:n("test/diagnostics"), roles:[n("work/support-gap-report")].into(),
 kinds:[Kind::WorkUse].into(),max_ttl_ms:Counter(30_000)
})].into() } }
struct SelfApprove;
impl WorkUsePort for SelfApprove {
 fn assess(&self,request:&WorkUseRequest)->WorkUseReply {
  let challenge=request.decision_request().unwrap().challenge(&n("test/no-private-key")).unwrap();
  let claim=challenge.claim(id(),Counter(30_000));
  let forged=SignedDecision {claim,signature:rx_package::SignatureEnvelope {key:n("test/no-private-key"),signature:"00".repeat(64)}};
  let error=challenge.verify(&forged).unwrap_err();
  assert_eq!(error,Failure::Signature);
  println!("host_counterfeit_signature={error}");
  WorkUseReply::Denied{decision_reference:n("test/host-cannot-issue"),conditions:[(n("work-use/host-self-issue"),error.to_string())].into()}
 }
}
fn main() {
 if std::env::args().any(|a|a=="--wire") {
  let data=std::fs::read("/evidence/wire-input.json").unwrap();
  let d=SignedDecision::decode(&data).unwrap();
  let reference=Reference {decision:d.claim.decision.clone(), kind:d.claim.challenge.kind, owner:d.claim.challenge.owner.clone(),issuer:d.claim.challenge.issuer.clone(),key:d.signature.key.clone(),epoch:d.claim.challenge.epoch.clone(),challenge:d.claim.challenge.id.clone(),context_digest:d.claim.challenge.context_digest,policy_digest:d.claim.challenge.policy_digest,signed_digest:Digest::from_bytes([3;32]),ttl_ms:d.claim.ttl_ms};
  let r=SignedRevocation{claim:RevocationClaim{schema:n("rx.external-decision-revocation.v1"),target:reference,reason:n("test/revoked")},signature:d.signature.clone()};
  let hex=|b:Vec<u8>| b.iter().map(|v|format!("{v:02x}")).collect::<String>();
  let failures=[Failure::Unconfigured,Failure::Policy,Failure::IssuerScope,Failure::Context,Failure::Kind,Failure::Epoch,Failure::Ttl,Failure::Expired,Failure::Revoked,Failure::Signature,Failure::Encoding,Failure::Identity,Failure::Capacity,Failure::Receiver].map(|v|v.to_string());
  let value=serde_json::json!({"decision":d,"revocation":r,"decision_message":hex(d.claim.signing_message(&d.signature.key).unwrap()),"revocation_message":hex(r.claim.signing_message(&r.signature.key).unwrap()),"failures":failures});
  println!("{}",String::from_utf8(rx_domain::canonical::bytes(&value).unwrap()).unwrap());return;
 }

 for (label,p,forged) in [("shipping-anchors-absent",None,false),("authored-anchor-null-provider",Some(policy()),false),("host-self-issuance",Some(policy()),true)] {
  let mut f=Fixture::new(p,true);let task=f.task(1000,6);
  let result=if forged {f.manager().prepare_work(task,&SelfApprove)} else {f.manager().prepare_work(task,&NoWorkUseProvider)};
  let error=result.unwrap_err().to_string();
  match label {"shipping-anchors-absent"=>assert!(error.contains("author-policy-absent")),"authored-anchor-null-provider"=>assert!(error.contains("Unsupported")),_=>assert!(error.contains("decision/signature"))}
  let rows=f.rows().iter().filter(|r|r.key.as_str().starts_with("work/")).count();assert_eq!(rows,0);
  println!("{}",serde_json::json!({"scene":label,"refusal":error,"work_rows":rows,"installed_release":true,"private_key_available_to_probe":false}));
 }
}
