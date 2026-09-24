use ed25519_dalek::{Signer, SigningKey};
use rx_domain::types::*;
use rx_package::*;
use std::{
    collections::BTreeMap,
};
fn name(s: &str) -> Name {
    Name::new(s).unwrap()
}
fn path(s: &str) -> PackagePath {
    PackagePath::new(s).unwrap()
}
fn contracts() -> ContractSet {
    ContractSet {
        base: Digest::from_bytes([1; 32]),
        cell: Digest::from_bytes([2; 32]),
        package_abi: name("rx.package-abi.v1"),
    }
}
fn target() -> Target {
    Target {
        os: OperatingSystem::Linux,
        architecture: Architecture::Amd64,
        ros_distribution: None,
    }
}
fn fixture() -> (
    Manifest,
    BTreeMap<PackagePath, Vec<u8>>,
    VerificationPolicy,
    SigningKey,
) {
    let key = SigningKey::from_bytes(&[42; 32]);
    let data = b"{\"schema\":\"rx.process-source.v1\"}".to_vec();
    let manifest = Manifest {
        schema: name("rx.package.v1"),
        package: name("example/tending"),
        version: "0.1.0".parse().unwrap(),
        publisher: name("example"),
        contracts: contracts(),
        targets: vec![target()],
        entry: EntryPoint::Process {
            source: path("process.json"),
        },
        permissions: vec![Permission::ArtifactRead],
        dependencies: vec![],
        assets: vec![],
        files: vec![FileEntry {
            path: path("process.json"),
            sha256: content_digest(&data),
            size_bytes: Counter(data.len() as u64),
            executable: false,
        }],
    };
    let trusted = TrustedPublisher {
        publisher: name("example"),
        verifying_key: key.verifying_key().to_bytes(),
        kinds: [PackageKind::Process, PackageKind::Ui, PackageKind::Device]
            .into_iter()
            .collect(),
        permissions: [
            Permission::ArtifactRead,
            Permission::NativeEndpoint { role: name("arm") },
            Permission::UiPanelRead {
                topic: name("overview"),
            },
        ]
        .into_iter()
        .collect(),
    };
    let policy = VerificationPolicy {
        additional_package_abis: Default::default(),
        publishers: BTreeMap::from([(name("test-key"), trusted)]),
        contracts: contracts(),
        target: target(),
        dependencies: BTreeMap::new(),
        assets: BTreeMap::new(),
        max_files: 128,
        max_content_bytes: 64 * 1024 * 1024,
    };
    (
        manifest,
        BTreeMap::from([(path("process.json"), data)]),
        policy,
        key,
    )
}
fn signed(manifest: &Manifest, key: &SigningKey) -> Vec<u8> {
    let key_id = name("test-key");
    let signature = key.sign(&signing_message(manifest, &key_id).unwrap());
    serde_json::to_vec(&SignatureEnvelope {
        key: key_id,
        signature: signature
            .to_bytes()
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect(),
    })
    .unwrap()
}
fn check(
    manifest: &Manifest,
    files: BTreeMap<PackagePath, Vec<u8>>,
    policy: &VerificationPolicy,
    key: &SigningKey,
) -> Result<VerifiedPackage> {
    verify_package(
        &serde_json::to_vec(manifest).unwrap(),
        &signed(manifest, key),
        files,
        policy,
    )
}


fn main() {
 let (manifest, files, policy, key) = fixture();
 let dir = std::path::Path::new("/tmp/policy-probe");
 std::fs::create_dir_all(dir).unwrap();
 let path = dir.join("policy.json");
 let mut document = rx_package::policy::Policy {
  schema:name("rx.package-verification-policy.v1"), additional_package_abis:vec![],
  contracts:contracts(), target:target(), keys:vec![], assets:vec![], dependencies:vec![],
 };
 std::fs::write(&path,serde_json::to_vec(&document).unwrap()).unwrap();
 let loaded:rx_package::policy::Policy=rx_package::policy::read(&path).unwrap();
 let before=check(&manifest,files.clone(),&loaded.load().unwrap(),&key);
 assert!(matches!(before,Err(Error::Untrusted)));
 println!("before_disk_key_injection=UNTRUSTED");
 let trusted=&policy.publishers[&name("test-key")];
 document.keys.push(rx_package::policy::Key {
  id:name("test-key"),publisher:trusted.publisher.clone(),
  verifying_key:Digest::from_bytes(trusted.verifying_key),kinds:trusted.kinds.clone(),permissions:trusted.permissions.clone(),
 });
 std::fs::write(&path,serde_json::to_vec(&document).unwrap()).unwrap();
 let loaded:rx_package::policy::Policy=rx_package::policy::read(&path).unwrap();
 check(&manifest,files,&loaded.load().unwrap(),&key).unwrap();
 println!("after_disk_key_injection=ACCEPTED; changed=policy.json; binary_unchanged=true; fixture_key_not_release_authority=true");
}
