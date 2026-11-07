# Key rotation runbook

Step 1: stop the writer in bin/writer.
Step 2: back up config/keys.txt.
Step 3: generate the new key pair.
Step 4: distribute the public key to readers.
Step 5: restart the writer and verify the first signed batch.
Step 6: revoke the old key only after the verification in step 5,
because revoking early locks out the readers that have not yet
