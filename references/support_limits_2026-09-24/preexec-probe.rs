// Isolated measurement only. No product file or SDK is edited by this probe.
use std::{io::{Read,Write},os::unix::{net::UnixStream,process::CommandExt},process::Command};
fn main(){
 let dir=tempfile::tempdir().unwrap();let path=dir.path().join("probe.db");
 let store=rx_storage::SqliteRepository::open(&path).unwrap();
 let (mut parent,mut child)=UnixStream::pair().unwrap();
 let thread=std::thread::spawn(move||{
  let mut command=Command::new("/bin/true");
  // Controlled pre-exec barrier: only socket read/write syscalls, no allocation,
  // lock acquisition or other application work occurs in the forked child.
  unsafe {command.pre_exec(move||{child.write_all(b"R")?;let mut b=[0];child.read_exact(&mut b)?;Ok(())});}
  command.spawn().unwrap()
 });
 let mut ready=[0];parent.read_exact(&mut ready).unwrap();assert_eq!(ready,[b'R']);
 drop(store);
 let error=match rx_storage::SqliteRepository::open(&path){Err(e)=>e.to_string(),Ok(_)=>panic!("original close-only repository unexpectedly reopened during pre-exec inheritance")};
 assert!(error.contains("would block"));
 parent.write_all(b"X").unwrap();let mut process=thread.join().unwrap();assert!(process.wait().unwrap().success());
 assert!(rx_storage::SqliteRepository::open(&path).is_ok());
 println!("RX_ACTUAL_COMMAND_PRE_EXEC_WINDOW: parent dropped unmodified product SqliteRepository; reopen refused before child exec: {error}; after child exec/exit reopen succeeded; no intentional pass_fd or stdin clone");
}
