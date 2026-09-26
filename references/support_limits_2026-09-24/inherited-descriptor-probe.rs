#[cfg(all(test, target_os="linux"))]
mod f12_inherited_lock_probe {
    #[test]
    fn dropped_rx_repository_can_remain_locked_by_inherited_descriptor() {
        use std::io::BufRead;
        let dir=tempfile::tempdir().unwrap();let path=dir.path().join("probe.db");
        let store=super::SqliteRepository::open(&path).unwrap();
        let inherited=store._ownership.try_clone().unwrap();
        let mut child=std::process::Command::new("/usr/bin/python3").args(["-c","import time; print('descriptor-held',flush=True); time.sleep(.5)"])
            .stdin(inherited).stdout(std::process::Stdio::piped()).spawn().unwrap();
        let mut line=String::new();std::io::BufReader::new(child.stdout.take().unwrap()).read_line(&mut line).unwrap();assert!(line.contains("descriptor-held"));
        drop(store);
        let refused=match super::SqliteRepository::open(&path){Err(e)=>e.to_string(),Ok(_)=>panic!("expected inherited-lock refusal")};
        assert!(refused.contains("would block"));assert!(child.wait().unwrap().success());
        assert!(super::SqliteRepository::open(&path).is_ok());
        println!("RX_REPOSITORY_INHERITED_FD_RETENTION: parent repository dropped; {refused}; reacquired after child exit; controlled descriptor-inheritance counterexample, not historical CI attribution");
    }
}
