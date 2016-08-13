for k, v in tpd.itercalls():
            try:
                if not v["Duration"]["value"]:
                    continue
                else:
                    if(int(v["Duration"]["value"])>0):
                        my_logger.debug("Duration data is true with no space value and no 0 value")
                    else:
                        continue
            except ValueError:
                # or calls with no duration
                continue
            entry = get_entry(k)
            if entry is None:
                entry = create_entry(k, JOURNAL_STATE_OPEN)
            else:
                if entry.get_state() == JOURNAL_STATE_CLOSED or k in closed_entries:
                    closed_calls.append(k)
                    continue
                elif entry.get_state() != JOURNAL_STATE_OPEN:
                    # not closed or open means something strange, probably
                    # requires support or dev examination and warrants
                    # halting execution
                    raise TelePresenceCommError(
                            "(device id: %s): unknown journal state " + \
                            "for entry key %s" % (tpd.did, k)
                            )
            entry.update_collected_data(v.to_entry())
            calls.append(entry)
