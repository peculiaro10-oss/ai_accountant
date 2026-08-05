raw_output = response.choices[0].message.content

                # 1. Remove think tags completely (case-insensitive and handles multi-line)
                clean_output = re.sub(r'<think>.*?</think>', '', raw_output, flags=re.DOTALL | re.IGNORECASE)
                
                # 2. Remove any leftover open/unclosed think tags if they appear
                clean_output = re.sub(r'</?think>', '', clean_output, flags=re.IGNORECASE)

                # 3. Strip out markdown asterisks (**) so they don't show up in Excel
                clean_output = clean_output.replace('**', '')

                clean_output = clean_output.strip()

                st.success("✅ Financial Processing Complete!")
                st.markdown(clean_output)

                # --- Spreadsheet Export Feature ---
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📥 Export Spreadsheet Report")
                
                csv_data = clean_output.encode("utf-8")
                
                st.download_button(
                    label="📥 Download Accounting Report as Spreadsheet (CSV)",
                    data=csv_data,
                    file_name="Financial_Accounting_Report.csv",
                    mime="text/csv",
                    use_container_width=True
                )