# JALM 1.0 "IntentDSL"  
**Date:** 2024-06-12  
**License:** MIT / JALM Foundation  

## 1. Design Mantra  
*"Write the thing you want, not the steps to make it."*

## 2. Textual Grammar (ABNF excerpt)  
```
intent   := directive*  begin  body  end
directive:= "import" | "expose" | "grant"
begin    := "BEGIN" id
body     := step+
step     := actor verb target [with params] [via channel] [when guard]
actor    := "$" ( system | client | api | template | timer )
verb     := "create" | "update" | "delete" | "run"
target   := uri | templateRef | serviceRef
params   := key ":" value
channel  := "web" | "email" | "sms" | "file" | "qr"
guard    := boolean expr
```

## 3. Vocabulary of Meta-Intents (pre-defined)  

| Intent Keyword            | Arity | Semantics                                                | Mini-Example |
|---------------------------|-------|----------------------------------------------------------|--------------|
| BEGIN                   | 1     | Opens an intent block, acts as root scope                | BEGIN booking-flow |
| IMPORT                  | 1+    | Pulls external template/tula by hash or tag             | IMPORT booking_widget v1.2 |
| GRANT                   | 2     | Scoped ACL on resource for an actor                    | GRANT client SELECT slots |
| EXPOSE                  | 1     | Public endpoint toggle                                 | EXPOSE /widget |
| RUN                     | 1+    | Execute atomic task (API step or inline)               | RUN validateSlot(slot_uuid) |
| CREATE                  | 1+    |  Declarative resource provisioning                      | CREATE database bookings |
| IF … THEN … ELSE … END  | 3     | Branching without explicit control flow                | IF error THEN sendSms ELSE sendEmail END |
| PARALLEL                | 1+    | Concurrent sub-flow                                    | PARALLEL notifySms notifyWebhook |
| ON ERROR                | 1     | Exception intent                                       | ON ERROR rollbackBooking |
| SCOPE Guard  END SCOPE  | 2     | Reversible shield around any sequence                  | SCOPE validatePayment END SCOPE |
| FOR EACH                | 2     | Map-reduce over iterable                               | FOR EACH booking IN today RUN "sendReminder(booking)" |
| SCHEDULE                | 3     | Cron-like intent                                       | SCHEDULE nightlyReport EVERY 1d AT 3:00 |
| DWELL                   | 1     | Idempotent retry with timeout sleep                    | DWELL 5s |
| VERSION (directive)     | 1     | SemVer pinning inside intent                           | VERSION 1.3.0-rc1 |

## 4. Minimal Valid Intent (full loop)
```
BEGIN booking-flow
  IMPORT booking_widget v1.3.2
  IMPORT slot_validator tula:hash~ab12fe
  GRANT client READ calendar slots
  EXPOSE /widget
  WHEN calendar_opens SCHEDULE notifyOpenSlots
  WHEN client REQUESTS slot
    RUN slot_uuid := slot_validator.create(slot) 
    IF slot_uuid OK THEN    
       PARALLEL 
          client.notify("confirmed", slot_uuid),
          system.log("evt: booked")    
    ELSE
       client.notify("choose_other")    
  ON ERROR rollbackBooking
END
```

## 5. Introspection Hooks  
Static introspection is possible directly in-text:  
```
@track
@cached 60s
BEGIN demo
```

## 6. Serialization Formats  
- **Canonical:** UTF-8 plain text .jalm (120 – 200 LOC typical)  
- **Derivative:** AST JSON, protobuf for wire transfer.

## 7. Runtime Contracts  
Executor (core-runner) guarantees:  
- determinism under identical scopes  
- 3 retry max unless overridden by DWELL 0s  
- scope isolation → replay on crash

---

**End-of-Spec.** 