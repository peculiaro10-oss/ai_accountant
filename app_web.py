# --- Professional Structured Excel Export with Subtotal Rows ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("📥 Export Official Audit Report")

                    current_date_str = datetime.now().strftime("%Y-%m-%d")
                    sanitized_org_name = statement.business_name.replace(" ", "_")
                    excel_filename = f"{sanitized_org_name}_Audit_{current_date_str}.xlsx"
                    
                    # Build a structured DataFrame with Category Blocks and Subtotals
                    export_rows = []
                    for cat in unique_categories:
                        df_cat_subset = df_result[df_result['category'] == cat]
                        
                        # Add category header row
                        export_rows.append({"date": f"--- CATEGORY: {cat.upper()} ---", "description": "", "category": "", "amount": ""})
                        
                        # Add rows for this category
                        for _, row in df_cat_subset.iterrows():
                            export_rows.append(row.to_dict())
                            
                        # Add subtotal row for this category
                        cat_subtotal = df_cat_subset['amount'].sum()
                        export_rows.append({"date": "", "description": f"SUBTOTAL FOR {cat.upper()}", "category": cat, "amount": cat_subtotal})
                        
                        # Add a blank spacing row
                        export_rows.append({"date": "", "description": "", "category": "", "amount": ""})

                    df_structured_export = pd.DataFrame(export_rows)

                    # Write to Excel and auto-fit column widths using openpyxl
                    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                        df_structured_export.to_excel(writer, sheet_name='Categorized Ledger', index=False)
                        
                        # Auto-adjust column widths so text never overlaps or clips
                        worksheet = writer.sheets['Categorized Ledger']
                        for col in worksheet.columns:
                            max_len = max(len(str(cell.value or '')) for cell in col)
                            col_letter = col[0].column_letter
                            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
                    
                    with open(excel_filename, "rb") as file_data:
                        st.download_button(
                            label="📥 Download Structured & Categorized Excel Report",
                            data=file_data,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )